"""Python AST parser for Odoo models, fields, methods, and controllers."""

import ast
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PythonParser:
    """Parser for Python files using AST."""

    def __init__(self, file_path: Path, module_name: str):
        """Initialize parser.

        Args:
            file_path: Path to Python file
            module_name: Odoo module name
        """
        self.file_path = file_path
        self.module_name = module_name
        self.relative_path = str(file_path)
        self.items = []

    def parse(self) -> list[dict]:
        """Parse Python file and extract Odoo elements.

        Returns:
            List of extracted items
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source, filename=str(self.file_path))
            self._visit_node(tree)
            return self.items

        except SyntaxError as e:
            logger.warning(f"Syntax error in {self.file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing {self.file_path}: {e}")
            return []

    def _visit_node(self, node: ast.AST, parent_class: Optional[str] = None):
        """Recursively visit AST nodes."""
        if isinstance(node, ast.ClassDef):
            self._process_class(node)
        elif isinstance(node, ast.FunctionDef) and parent_class:
            # Process methods inside classes
            pass  # Handled in _process_class

        # Continue traversing
        for child in ast.iter_child_nodes(node):
            self._visit_node(child, parent_class)

    def _process_class(self, node: ast.ClassDef):
        """Process a class definition (Model or Controller)."""
        # Check if it's an Odoo model
        if self._is_odoo_model(node):
            self._extract_model(node)
        elif self._is_controller(node):
            self._extract_controller(node)

    def _is_odoo_model(self, node: ast.ClassDef) -> bool:
        """Check if class inherits from models.Model."""
        for base in node.bases:
            base_name = self._get_name(base)
            if base_name in ('models.Model', 'models.TransientModel', 'models.AbstractModel'):
                return True
        return False

    def _is_controller(self, node: ast.ClassDef) -> bool:
        """Check if class inherits from http.Controller."""
        for base in node.bases:
            base_name = self._get_name(base)
            if base_name in ('http.Controller', 'Controller'):
                return True
        return False

    def _extract_model(self, node: ast.ClassDef):
        """Extract model information from class."""
        # Get model attributes
        model_name = None
        description = None
        inherits = []
        inherits_models = {}
        is_transient = False
        is_abstract = False

        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attr_name = target.id
                        value = self._get_value(item.value)

                        if attr_name == '_name':
                            model_name = value
                        elif attr_name == '_description':
                            description = value
                        elif attr_name == '_inherit':
                            if isinstance(value, list):
                                inherits = value
                            elif value:
                                inherits = [value]
                        elif attr_name == '_inherits':
                            inherits_models = value if isinstance(value, dict) else {}
                        elif attr_name == '_transient' and value is True:
                            is_transient = True
                        elif attr_name == '_abstract' and value is True:
                            is_abstract = True

        # Determine model type
        model_type = 'abstract' if is_abstract else ('transient' if is_transient else 'regular')

        # If has _inherit and either:
        # 1. No _name (classic extension pattern)
        # 2. _name matches one of the inherited models (extending existing model)
        is_extension = bool(inherits) and (model_name is None or model_name in inherits)

        if is_extension:
            # For extensions, use the inherited model name
            model_name = inherits[0] if inherits else None

        if not model_name:
            return  # Skip classes without _name or _inherit

        # Add model item
        self.items.append({
            'item_type': 'model',
            'name': model_name,
            'parent_name': None,
            'module': self.module_name,
            'attributes': {
                'description': description or '',
                'model_type': model_type,
                'inherits': inherits,
                'inherits_models': inherits_models
            },
            'references': [{
                'file_path': self.relative_path,
                'line_number': node.lineno,
                'reference_type': 'inheritance' if is_extension else 'definition',
                'context': node.name
            }]
        })

        # Extract fields and methods
        self._extract_fields(node, model_name)
        self._extract_methods(node, model_name)

    def _extract_fields(self, node: ast.ClassDef, model_name: str):
        """Extract field definitions from model class."""
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        field_name = target.id

                        # Check if it's a field assignment
                        if isinstance(item.value, ast.Call):
                            field_type = self._get_field_type(item.value)
                            if field_type:
                                attributes = self._extract_field_attributes(item.value, field_type)

                                self.items.append({
                                    'item_type': 'field',
                                    'name': field_name,
                                    'parent_name': model_name,
                                    'module': self.module_name,
                                    'attributes': attributes,
                                    'references': [{
                                        'file_path': self.relative_path,
                                        'line_number': item.lineno,
                                        'reference_type': 'definition',
                                        'context': field_name
                                    }]
                                })

    def _get_field_type(self, call_node: ast.Call) -> Optional[str]:
        """Get field type from call node."""
        if isinstance(call_node.func, ast.Attribute):
            # fields.Char(), fields.Many2one(), etc.
            if isinstance(call_node.func.value, ast.Name):
                if call_node.func.value.id == 'fields':
                    return call_node.func.attr
        elif isinstance(call_node.func, ast.Name):
            # Direct Field type reference
            field_types = ['Char', 'Text', 'Integer', 'Float', 'Boolean', 'Date', 'Datetime',
                          'Many2one', 'One2many', 'Many2many', 'Selection', 'Binary', 'Html',
                          'Monetary', 'Reference', 'Json']
            if call_node.func.id in field_types:
                return call_node.func.id
        return None

    def _extract_field_attributes(self, call_node: ast.Call, field_type: str) -> dict:
        """Extract field attributes from field definition."""
        attributes = {'field_type': field_type}

        # Extract keyword arguments
        for keyword in call_node.keywords:
            key = keyword.arg
            value = self._get_value(keyword.value)

            if key == 'string':
                attributes['string'] = value
            elif key == 'required':
                attributes['required'] = value
            elif key == 'readonly':
                attributes['readonly'] = value
            elif key == 'compute':
                attributes['compute'] = value
            elif key == 'related':
                attributes['related'] = value
            elif key == 'default':
                attributes['default'] = str(value)[:100] if value else None
            elif key == 'comodel_name':
                attributes['comodel_name'] = value
            elif key == 'selection':
                attributes['selection'] = value if isinstance(value, list) else None
            elif key == 'help':
                attributes['help'] = value
            elif key == 'store':
                attributes['store'] = value
            elif key == 'track_visibility':
                attributes['track_visibility'] = value

        return attributes

    def _extract_methods(self, node: ast.ClassDef, model_name: str):
        """Extract method definitions from model class."""
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Skip private methods (starting with _) unless they are special
                if item.name.startswith('_') and not item.name.startswith('__'):
                    # Include compute methods and important private methods
                    pass

                decorators = self._extract_decorators(item)

                self.items.append({
                    'item_type': 'function',
                    'name': item.name,
                    'parent_name': model_name,
                    'module': self.module_name,
                    'attributes': {
                        'decorators': decorators,
                        'parameters': [arg.arg for arg in item.args.args]
                    },
                    'references': [{
                        'file_path': self.relative_path,
                        'line_number': item.lineno,
                        'reference_type': 'definition',
                        'context': item.name
                    }]
                })

    def _extract_decorators(self, func_node: ast.FunctionDef) -> list[str]:
        """Extract decorator strings from function."""
        decorators = []
        for decorator in func_node.decorator_list:
            dec_str = self._decorator_to_string(decorator)
            if dec_str:
                decorators.append(dec_str)
        return decorators

    def _decorator_to_string(self, node: ast.AST) -> Optional[str]:
        """Convert decorator AST node to string."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            func_name = self._decorator_to_string(node.func)
            # Get arguments
            args = [self._get_value(arg) for arg in node.args]
            args_str = ', '.join(repr(arg) for arg in args if arg)
            return f"{func_name}({args_str})" if args_str else func_name
        return None

    def _extract_controller(self, node: ast.ClassDef):
        """Extract controller routes from class."""
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Look for @http.route decorator
                for decorator in item.decorator_list:
                    route_info = self._extract_route_info(decorator)
                    if route_info:
                        self.items.append({
                            'item_type': 'controller_route',
                            'name': route_info['route'],
                            'parent_name': f"{node.name}.{item.name}",
                            'module': self.module_name,
                            'attributes': route_info,
                            'references': [{
                                'file_path': self.relative_path,
                                'line_number': item.lineno,
                                'reference_type': 'definition',
                                'context': item.name
                            }]
                        })

    def _extract_route_info(self, decorator: ast.AST) -> Optional[dict]:
        """Extract route information from decorator."""
        if isinstance(decorator, ast.Call):
            func_name = self._get_name(decorator.func)
            if func_name in ('http.route', 'route'):
                route = None
                methods = ['GET']
                auth = 'user'
                route_type = 'http'

                # First positional argument is route
                if decorator.args:
                    route = self._get_value(decorator.args[0])

                # Extract keyword arguments
                for keyword in decorator.keywords:
                    key = keyword.arg
                    value = self._get_value(keyword.value)

                    if key == 'methods':
                        methods = value if isinstance(value, list) else [value]
                    elif key == 'auth':
                        auth = value
                    elif key == 'type':
                        route_type = value

                if route:
                    return {
                        'route': route,
                        'methods': methods,
                        'auth': auth,
                        'type': route_type
                    }

        return None

    def _get_name(self, node: ast.AST) -> str:
        """Get name from various AST node types."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_name(node.value)
            return f"{value}.{node.attr}" if value else node.attr
        return ''

    def _get_value(self, node: ast.AST):
        """Extract value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.List):
            return [self._get_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Tuple):
            return [self._get_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Dict):
            return {
                self._get_value(k): self._get_value(v)
                for k, v in zip(node.keys, node.values)
            }
        elif isinstance(node, ast.Name):
            if node.id in ('True', 'False', 'None'):
                return {'True': True, 'False': False, 'None': None}[node.id]
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_name(node)
        elif isinstance(node, ast.Lambda):
            return '<lambda>'
        elif isinstance(node, ast.Call):
            return f"<call:{self._get_name(node.func)}>"
        return None


def parse_python_file(file_path: Path, module_name: str) -> list[dict]:
    """Parse a Python file and extract Odoo elements.

    Args:
        file_path: Path to Python file
        module_name: Odoo module name

    Returns:
        List of extracted items
    """
    parser = PythonParser(file_path, module_name)
    return parser.parse()
