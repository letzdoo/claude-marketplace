"""Module dependency tree builder and depth calculator."""

import logging
from collections import defaultdict, deque
from pathlib import Path
from typing import Optional

from parsers.manifest_parser import parse_manifest

logger = logging.getLogger(__name__)


class ModuleDependencyTree:
    """Builds and analyzes module dependency tree."""

    def __init__(self, modules: dict[str, Path]):
        """Initialize dependency tree builder.

        Args:
            modules: Dict mapping module names to their paths
        """
        self.modules = modules
        self.dependencies: dict[str, list[str]] = {}
        self.depths: dict[str, int] = {}
        self._build_dependency_graph()
        self._calculate_depths()

    def _build_dependency_graph(self):
        """Build dependency graph from all manifests."""
        logger.info("Building module dependency graph...")

        for module_name, module_path in self.modules.items():
            # Find manifest file
            manifest_path = module_path / '__manifest__.py'
            if not manifest_path.exists():
                manifest_path = module_path / '__openerp__.py'

            if not manifest_path.exists():
                logger.warning(f"No manifest found for module: {module_name}")
                self.dependencies[module_name] = []
                continue

            # Parse manifest
            manifest_item = parse_manifest(manifest_path, module_name)
            if manifest_item and 'attributes' in manifest_item:
                depends = manifest_item['attributes'].get('depends', [])
                # Filter out dependencies that don't exist in our module list
                # (this handles external/missing dependencies)
                valid_depends = [dep for dep in depends if dep in self.modules or dep == 'base']
                self.dependencies[module_name] = valid_depends
            else:
                logger.warning(f"Could not parse manifest for module: {module_name}")
                self.dependencies[module_name] = []

        logger.info(f"Built dependency graph with {len(self.dependencies)} modules")

    def _calculate_depths(self):
        """Calculate dependency depth for each module using BFS.

        Depth is defined as the longest path from a base module (depth 0) to the target module.
        Base modules are those with no dependencies or only depending on 'base'.
        """
        logger.info("Calculating module dependency depths...")

        # Initialize all depths to None (unvisited)
        self.depths = {}

        # Find all base modules (no dependencies or only 'base')
        base_modules = set()
        for module_name, deps in self.dependencies.items():
            if not deps or (len(deps) == 1 and deps[0] == 'base'):
                base_modules.add(module_name)
                self.depths[module_name] = 0

        # Also treat 'base' itself as depth 0 (even if not in our module list)
        if 'base' in self.modules:
            self.depths['base'] = 0
            base_modules.add('base')

        logger.info(f"Found {len(base_modules)} base modules")

        # Build reverse dependency graph (who depends on me)
        reverse_deps: dict[str, list[str]] = defaultdict(list)
        for module_name, deps in self.dependencies.items():
            for dep in deps:
                reverse_deps[dep].append(module_name)

        # BFS to calculate depths
        queue = deque(base_modules)
        visited = set(base_modules)

        while queue:
            current_module = queue.popleft()
            current_depth = self.depths.get(current_module, 0)

            # Process all modules that depend on current_module
            for dependent in reverse_deps[current_module]:
                # Calculate the depth for this dependent
                # It should be max(all dependency depths) + 1
                dep_depths = []
                for dep in self.dependencies[dependent]:
                    if dep in self.depths:
                        dep_depths.append(self.depths[dep])
                    else:
                        # Dependency not yet visited, treat as 0
                        dep_depths.append(0)

                new_depth = max(dep_depths) + 1 if dep_depths else 0

                # Update depth if we found a longer path
                if dependent not in self.depths or new_depth > self.depths[dependent]:
                    self.depths[dependent] = new_depth

                # Add to queue if not visited
                if dependent not in visited:
                    visited.add(dependent)
                    queue.append(dependent)

        # Handle any modules that weren't reached (circular dependencies or isolated modules)
        for module_name in self.dependencies:
            if module_name not in self.depths:
                logger.warning(f"Module {module_name} has no depth assigned (circular dependency?), setting to 0")
                self.depths[module_name] = 0

        # Log depth statistics
        depth_counts = defaultdict(int)
        for depth in self.depths.values():
            depth_counts[depth] += 1

        logger.info("Dependency depth distribution:")
        for depth in sorted(depth_counts.keys()):
            logger.info(f"  Depth {depth}: {depth_counts[depth]} modules")

    def get_depth(self, module_name: str) -> int:
        """Get dependency depth for a module.

        Args:
            module_name: Module name

        Returns:
            Dependency depth (0 for base modules, higher for dependent modules)
        """
        return self.depths.get(module_name, 0)

    def get_dependencies(self, module_name: str) -> list[str]:
        """Get direct dependencies for a module.

        Args:
            module_name: Module name

        Returns:
            List of direct dependency module names
        """
        return self.dependencies.get(module_name, [])

    def get_depth_stats(self) -> dict:
        """Get statistics about dependency depths.

        Returns:
            Dict with depth statistics
        """
        if not self.depths:
            return {'total_modules': 0, 'max_depth': 0, 'depth_distribution': {}}

        depth_distribution = defaultdict(int)
        for depth in self.depths.values():
            depth_distribution[depth] += 1

        return {
            'total_modules': len(self.depths),
            'max_depth': max(self.depths.values()) if self.depths else 0,
            'depth_distribution': dict(depth_distribution)
        }
