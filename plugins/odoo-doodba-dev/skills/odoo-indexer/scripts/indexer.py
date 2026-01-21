"""Main indexer for Odoo codebase."""

import asyncio
import hashlib
import logging
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from typing import Optional

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

import config
from database import Database
from dependency_tree import ModuleDependencyTree
from parsers.python_parser import parse_python_file
from parsers.xml_parser import parse_xml_file
from parsers.csv_parser import parse_access_csv
from parsers.manifest_parser import parse_manifest

logger = logging.getLogger(__name__)


# Wrapper functions for multiprocessing (must be picklable)
def _parse_file_worker(file_path: Path, module_name: str) -> tuple[Path, list[dict]]:
    """Worker function to parse a file in a separate process.

    Args:
        file_path: Path to file
        module_name: Module name

    Returns:
        Tuple of (file_path, parsed_items)
    """
    try:
        if file_path.suffix == '.py':
            items = parse_python_file(file_path, module_name)
        elif file_path.suffix == '.xml':
            items = parse_xml_file(file_path, module_name)
        elif file_path.suffix == '.csv' and 'security' in file_path.parts:
            items = parse_access_csv(file_path, module_name)
        else:
            items = []
        return (file_path, items)
    except Exception as e:
        logger.error(f"Error parsing {file_path}: {e}")
        return (file_path, [])


class OdooIndexer:
    """Odoo codebase indexer."""

    def __init__(self, db: Database):
        """Initialize indexer.

        Args:
            db: Database instance
        """
        self.db = db
        self.odoo_path = config.ODOO_PATH
        self.process_pool: Optional[ProcessPoolExecutor] = None
        self.dependency_tree: Optional[ModuleDependencyTree] = None

    async def index_all_modules(self, incremental: bool = True, module_filter: Optional[list[str]] = None):
        """Index all Odoo modules.

        Args:
            incremental: If True, skip unchanged files
            module_filter: List of module names to index (None = all modules)
        """
        logger.info(f"Starting indexing of {self.odoo_path}")

        # Discover modules
        all_modules = self._discover_modules()

        # Build dependency tree from ALL modules for accurate depth calculation
        logger.info("Building module dependency tree...")
        self.dependency_tree = ModuleDependencyTree(all_modules)
        depth_stats = self.dependency_tree.get_depth_stats()
        logger.info(f"Dependency tree built: {depth_stats['total_modules']} modules, "
                   f"max depth: {depth_stats['max_depth']}")

        # Filter modules for indexing AFTER building dependency tree
        if module_filter:
            modules = {name: path for name, path in all_modules.items() if name in module_filter}
        else:
            modules = all_modules

        logger.info(f"Found {len(modules)} modules to index")

        # Create persistent thread pool (ThreadPool is more compatible with asyncio/uvloop)
        max_workers = config.MAX_WORKER_PROCESSES if config.MAX_WORKER_PROCESSES > 0 else os.cpu_count()
        logger.info(f"Creating thread pool with {max_workers} workers")

        self.process_pool = ThreadPoolExecutor(max_workers=max_workers)

        try:
            # Index modules concurrently
            semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_MODULES)
            completed_count = 0
            total_count = len(modules)

            async def index_with_semaphore(module_name: str, module_path: Path):
                nonlocal completed_count
                async with semaphore:
                    try:
                        await self.index_module(module_name, module_path, incremental)
                        completed_count += 1
                        if completed_count % 10 == 0 or completed_count == total_count:
                            logger.info(f"Progress: {completed_count}/{total_count} modules indexed")
                    except Exception as e:
                        logger.error(f"Failed to index module {module_name}: {e}", exc_info=True)
                        completed_count += 1

            tasks = [
                index_with_semaphore(module_name, module_path)
                for module_name, module_path in modules.items()
            ]

            await asyncio.gather(*tasks)
        finally:
            # Shutdown thread pool
            logger.info("Shutting down thread pool")
            self.process_pool.shutdown(wait=True)
            self.process_pool = None

        # Close the async connection pool
        await self.db.close_pool()

        logger.info("Indexing complete")

    def _discover_modules(self) -> dict[str, Path]:
        """Discover all Odoo modules.

        Returns:
            Dict mapping module names to their paths
        """
        modules = {}

        # Find all __manifest__.py files
        for manifest_path in self.odoo_path.rglob('__manifest__.py'):
            module_path = manifest_path.parent
            module_name = module_path.name
            modules[module_name] = module_path

        # Also check for __openerp__.py (older Odoo versions)
        for manifest_path in self.odoo_path.rglob('__openerp__.py'):
            module_path = manifest_path.parent
            module_name = module_path.name
            if module_name not in modules:
                modules[module_name] = module_path

        return modules

    async def index_module(self, module_name: str, module_path: Path, incremental: bool = True):
        """Index a single Odoo module.

        Args:
            module_name: Module name
            module_path: Path to module directory
            incremental: If True, skip unchanged files
        """
        logger.info(f"[START] Indexing module: {module_name}")

        try:
            # First, index the manifest
            manifest_path = module_path / '__manifest__.py'
            if not manifest_path.exists():
                manifest_path = module_path / '__openerp__.py'

            if manifest_path.exists():
                manifest_item = parse_manifest(manifest_path, module_name)
                if manifest_item:
                    module_depth = self.dependency_tree.get_depth(module_name) if self.dependency_tree else 0
                    await self._store_items([manifest_item], str(manifest_path), module_name, module_depth=module_depth)

            # Find all Python, XML, and CSV files
            files_to_index = []

            for pattern in ['**/*.py', '**/*.xml', '**/security/*.csv']:
                for file_path in module_path.glob(pattern):
                    if file_path.name in ('__manifest__.py', '__openerp__.py', '__init__.py'):
                        continue
                    files_to_index.append(file_path)

            # Filter files for incremental indexing
            if incremental:
                filtered_files = []
                for file_path in files_to_index:
                    relative_path = str(file_path.relative_to(self.odoo_path))
                    file_hash = self._calculate_file_hash(file_path)
                    stored_hash = await self.db.get_file_hash_async(relative_path)
                    if stored_hash != file_hash:
                        filtered_files.append(file_path)
                    else:
                        logger.debug(f"Skipping unchanged file: {relative_path}")
                files_to_index = filtered_files

            if not files_to_index:
                logger.info(f"[DONE] Module {module_name}: No files to index")
                return

            logger.info(f"[PARSING] Module {module_name}: {len(files_to_index)} files")

            # Parse all files in parallel using the persistent thread pool
            loop = asyncio.get_running_loop()
            parse_tasks = [
                loop.run_in_executor(self.process_pool, _parse_file_worker, file_path, module_name)
                for file_path in files_to_index
            ]
            try:
                results = await asyncio.gather(*parse_tasks, return_exceptions=True)
            except Exception as e:
                logger.error(f"[ERROR] Failed to gather parse results for {module_name}: {e}", exc_info=True)
                raise

            logger.info(f"[PARSED] Module {module_name}: {len(results)} results")

            # Store results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error in parsing task: {result}")
                    continue

                file_path, items = result
                if items:
                    relative_path = str(file_path.relative_to(self.odoo_path))
                    file_hash = self._calculate_file_hash(file_path)
                    module_depth = self.dependency_tree.get_depth(module_name) if self.dependency_tree else 0
                    await self._store_items(items, relative_path, module_name, file_hash, module_depth)
                    logger.debug(f"Indexed {len(items)} items from {relative_path}")

            logger.info(f"[COMPLETE] Module {module_name}: indexed successfully")

        except Exception as e:
            logger.error(f"[ERROR] Module {module_name}: {e}", exc_info=True)


    async def _store_items(self, items: list[dict], file_path: str, module_name: str,
                          file_hash: Optional[str] = None, module_depth: int = 0):
        """Store items in database asynchronously (one transaction per file).

        Args:
            items: List of items to store
            file_path: File path
            module_name: Module name
            file_hash: File hash for change tracking
            module_depth: Module dependency depth
        """
        # Use async database operations directly
        await self.db.store_items_async(items, file_path, module_name, file_hash, module_depth)

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file.

        Args:
            file_path: Path to file

        Returns:
            MD5 hash as hex string
        """
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()


async def index_odoo_codebase(incremental: bool = True, module_filter: Optional[list[str]] = None,
                              clear_db: bool = False):
    """Index Odoo codebase.

    Args:
        incremental: If True, skip unchanged files
        module_filter: List of module names to index (None = all)
        clear_db: If True, clear database before indexing
    """
    db = Database(config.SQLITE_DB_PATH)

    if clear_db:
        logger.info("Clearing database")
        db.clear_all()

    indexer = OdooIndexer(db)
    await indexer.index_all_modules(incremental, module_filter)
