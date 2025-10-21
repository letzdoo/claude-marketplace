"""XML parser for Odoo views, menus, actions, rules, and data records."""

from lxml import etree
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class XMLParser:
    """Parser for XML files."""

    def __init__(self, file_path: Path, module_name: str):
        """Initialize parser.

        Args:
            file_path: Path to XML file
            module_name: Odoo module name
        """
        self.file_path = file_path
        self.module_name = module_name
        self.relative_path = str(file_path)
        self.items = []

    def parse(self) -> list[dict]:
        """Parse XML file and extract Odoo elements.

        Returns:
            List of extracted items
        """
        try:
            # Parse XML with lxml (automatically tracks line numbers)
            parser = etree.XMLParser(remove_blank_text=False, recover=True)
            tree = etree.parse(str(self.file_path), parser)
            root = tree.getroot()

            self._process_element(root)

            return self.items

        except etree.XMLSyntaxError as e:
            logger.warning(f"XML parse error in {self.file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing {self.file_path}: {e}")
            return []

    def _get_line_number(self, element) -> int:
        """Get line number for an element using lxml's sourceline."""
        return getattr(element, 'sourceline', 1)

    def _process_element(self, element, parent_path: str = ''):
        """Recursively process XML elements."""
        # Process based on element type
        if element.tag == 'record':
            self._extract_record(element)
        elif element.tag == 'menuitem':
            self._extract_menuitem(element)
        elif element.tag == 'template':
            self._extract_template(element)

        # Continue traversing
        for child in element:
            self._process_element(child, parent_path)

    def _extract_record(self, element):
        """Extract record information."""
        record_id = element.get('id', '')
        model = element.get('model', '')

        if not model:
            return

        # Get name field if present
        name = None
        for field in element.findall('field'):
            if field.get('name') == 'name':
                name = field.text or field.get('eval', '')
                break

        line_number = self._get_line_number(element)

        # Determine record type and extract specific info
        if model == 'ir.ui.view':
            self._extract_view(element, record_id, name, line_number)
        elif model.startswith('ir.actions.'):
            self._extract_action(element, record_id, name, line_number, model)
        elif model == 'ir.rule':
            self._extract_rule(element, record_id, name, line_number)
        elif model == 'ir.cron':
            self._extract_cron(element, record_id, name, line_number)
        elif model == 'ir.model.access':
            self._extract_access_right(element, record_id, name, line_number)
        else:
            # Generic XML ID
            self._extract_xml_id(element, record_id, name, line_number, model)

    def _extract_view(self, element, xml_id: str, name: Optional[str], line_number: int):
        """Extract view information."""
        # Get view fields
        view_type = None
        model = None
        inherit_id = None
        priority = 16
        groups = []
        mode = 'primary'

        for field in element.findall('field'):
            field_name = field.get('name')
            field_value = field.text or field.get('ref', '') or field.get('eval', '')

            if field_name == 'type':
                view_type = field_value
            elif field_name == 'model':
                model = field_value
            elif field_name == 'inherit_id':
                inherit_id = field.get('ref', field_value)
                mode = 'extension'
            elif field_name == 'priority':
                try:
                    priority = int(field_value)
                except ValueError:
                    pass
            elif field_name == 'groups_id':
                groups_ref = field.get('ref', '')
                if groups_ref:
                    groups = [g.strip() for g in groups_ref.split(',')]
            elif field_name == 'arch':
                # Detect view type from arch if not explicitly set
                if not view_type and len(field):
                    for child in field:
                        if child.tag in ('form', 'tree', 'kanban', 'search', 'graph', 'pivot', 'calendar', 'gantt', 'qweb'):
                            view_type = child.tag
                            break

        self.items.append({
            'item_type': 'view',
            'name': xml_id,
            'parent_name': None,
            'module': self.module_name,
            'attributes': {
                'view_type': view_type or 'unknown',
                'model': model or '',
                'inherit_id': inherit_id,
                'priority': priority,
                'groups': groups,
                'mode': mode,
                'display_name': name or xml_id
            },
            'references': [{
                'file_path': self.relative_path,
                'line_number': line_number,
                'reference_type': 'definition',
                'context': xml_id
            }]
        })

    def _extract_action(self, element, xml_id: str, name: Optional[str],
                       line_number: int, model: str):
        """Extract action information."""
        action_type = model.replace('ir.actions.', '')

        # Get action fields
        res_model = None
        view_mode = None
        domain = None
        context = None
        target = 'current'
        report_name = None
        report_type = None

        for field in element.findall('field'):
            field_name = field.get('name')
            field_value = field.text or field.get('eval', '')

            if field_name == 'res_model':
                res_model = field_value
            elif field_name == 'view_mode':
                view_mode = field_value
            elif field_name == 'domain':
                domain = field_value
            elif field_name == 'context':
                context = field_value
            elif field_name == 'target':
                target = field_value
            elif field_name == 'report_name':
                report_name = field_value
            elif field_name == 'report_type':
                report_type = field_value

        self.items.append({
            'item_type': 'action',
            'name': xml_id,
            'parent_name': None,
            'module': self.module_name,
            'attributes': {
                'action_type': action_type,
                'res_model': res_model,
                'view_mode': view_mode,
                'domain': domain,
                'context': context,
                'target': target,
                'report_name': report_name,
                'report_type': report_type,
                'display_name': name or xml_id
            },
            'references': [{
                'file_path': self.relative_path,
                'line_number': line_number,
                'reference_type': 'definition',
                'context': xml_id
            }]
        })

    def _extract_menuitem(self, element):
        """Extract menu item information."""
        menu_id = element.get('id', '')
        name = element.get('name', '')
        parent = element.get('parent', '')
        action = element.get('action', '')
        sequence = element.get('sequence', '10')
        groups = element.get('groups', '')
        web_icon = element.get('web_icon', '')

        line_number = self._get_line_number(element)

        groups_list = [g.strip() for g in groups.split(',') if g.strip()]

        self.items.append({
            'item_type': 'menu',
            'name': menu_id,
            'parent_name': None,
            'module': self.module_name,
            'attributes': {
                'display_name': name,
                'parent_id': parent,
                'action': action,
                'sequence': int(sequence) if sequence.isdigit() else 10,
                'groups': groups_list,
                'web_icon': web_icon
            },
            'references': [{
                'file_path': self.relative_path,
                'line_number': line_number,
                'reference_type': 'definition',
                'context': menu_id
            }]
        })

    def _extract_rule(self, element, xml_id: str, name: Optional[str], line_number: int):
        """Extract record rule information."""
        # Get rule fields
        model_id = None
        domain_force = None
        groups = []
        perm_read = True
        perm_write = True
        perm_create = True
        perm_unlink = True
        is_global = False

        for field in element.findall('field'):
            field_name = field.get('name')
            field_value = field.text or field.get('ref', '') or field.get('eval', '')

            if field_name == 'model_id':
                # Extract model name from ref
                model_ref = field.get('ref', '')
                if model_ref.startswith('model_'):
                    model_id = model_ref.replace('model_', '').replace('_', '.')
            elif field_name == 'domain_force':
                domain_force = field_value
            elif field_name == 'groups':
                groups_ref = field.get('ref', '')
                if groups_ref:
                    groups = [g.strip() for g in groups_ref.split(',')]
            elif field_name == 'perm_read':
                perm_read = field_value.lower() in ('true', '1')
            elif field_name == 'perm_write':
                perm_write = field_value.lower() in ('true', '1')
            elif field_name == 'perm_create':
                perm_create = field_value.lower() in ('true', '1')
            elif field_name == 'perm_unlink':
                perm_unlink = field_value.lower() in ('true', '1')
            elif field_name == 'global':
                is_global = field_value.lower() in ('true', '1')

        self.items.append({
            'item_type': 'record_rule',
            'name': xml_id,
            'parent_name': None,
            'module': self.module_name,
            'attributes': {
                'model_name': model_id or '',
                'domain_force': domain_force,
                'groups': groups,
                'perm_read': perm_read,
                'perm_write': perm_write,
                'perm_create': perm_create,
                'perm_unlink': perm_unlink,
                'global': is_global,
                'display_name': name or xml_id
            },
            'references': [{
                'file_path': self.relative_path,
                'line_number': line_number,
                'reference_type': 'definition',
                'context': xml_id
            }]
        })

    def _extract_cron(self, element, xml_id: str, name: Optional[str], line_number: int):
        """Extract scheduled action (cron) information."""
        # Get cron fields
        model_name = None
        function = None
        interval_type = 'days'
        interval_number = 1
        numbercall = -1
        active = True

        for field in element.findall('field'):
            field_name = field.get('name')
            field_value = field.text or field.get('eval', '')

            if field_name == 'model_id':
                model_ref = field.get('ref', '')
                if model_ref.startswith('model_'):
                    model_name = model_ref.replace('model_', '').replace('_', '.')
            elif field_name == 'code':
                # Extract function name from code
                if 'model.' in field_value:
                    parts = field_value.split('.')
                    if len(parts) >= 2:
                        function = parts[1].split('(')[0]
            elif field_name == 'function':
                function = field_value
            elif field_name == 'interval_type':
                interval_type = field_value
            elif field_name == 'interval_number':
                try:
                    interval_number = int(field_value)
                except ValueError:
                    pass
            elif field_name == 'numbercall':
                try:
                    numbercall = int(field_value)
                except ValueError:
                    pass
            elif field_name == 'active':
                active = field_value.lower() in ('true', '1')

        self.items.append({
            'item_type': 'scheduled_action',
            'name': xml_id,
            'parent_name': None,
            'module': self.module_name,
            'attributes': {
                'model_name': model_name or '',
                'function': function or '',
                'interval_type': interval_type,
                'interval_number': interval_number,
                'numbercall': numbercall,
                'active': active,
                'display_name': name or xml_id
            },
            'references': [{
                'file_path': self.relative_path,
                'line_number': line_number,
                'reference_type': 'definition',
                'context': xml_id
            }]
        })

    def _extract_template(self, element):
        """Extract QWeb template information."""
        template_id = element.get('id', '')
        name = element.get('name', '') or element.get('t-name', '')

        line_number = self._get_line_number(element)

        # Determine if it's a report template
        is_report = 'report' in template_id.lower() or 'report' in name.lower()

        self.items.append({
            'item_type': 'report_template',
            'name': template_id,
            'parent_name': None,
            'module': self.module_name,
            'attributes': {
                'template_name': name,
                'is_report': is_report,
                'display_name': name or template_id
            },
            'references': [{
                'file_path': self.relative_path,
                'line_number': line_number,
                'reference_type': 'definition',
                'context': template_id
            }]
        })

    def _extract_access_right(self, element, xml_id: str, name: Optional[str], line_number: int):
        """Extract access right information."""
        # Get access right fields
        model_name = None
        group = None
        perm_read = False
        perm_write = False
        perm_create = False
        perm_unlink = False

        for field in element.findall('field'):
            field_name = field.get('name')
            field_value = field.text or field.get('ref', '') or field.get('eval', '')

            if field_name == 'model_id':
                model_ref = field.get('ref', '')
                if model_ref.startswith('model_'):
                    model_name = model_ref.replace('model_', '').replace('_', '.')
            elif field_name == 'group_id':
                group = field.get('ref', field_value)
            elif field_name == 'perm_read':
                perm_read = field_value.lower() in ('true', '1')
            elif field_name == 'perm_write':
                perm_write = field_value.lower() in ('true', '1')
            elif field_name == 'perm_create':
                perm_create = field_value.lower() in ('true', '1')
            elif field_name == 'perm_unlink':
                perm_unlink = field_value.lower() in ('true', '1')

        self.items.append({
            'item_type': 'access_right',
            'name': xml_id,
            'parent_name': None,
            'module': self.module_name,
            'attributes': {
                'model_name': model_name or '',
                'group': group,
                'perm_read': perm_read,
                'perm_write': perm_write,
                'perm_create': perm_create,
                'perm_unlink': perm_unlink,
                'display_name': name or xml_id
            },
            'references': [{
                'file_path': self.relative_path,
                'line_number': line_number,
                'reference_type': 'definition',
                'context': xml_id
            }]
        })

    def _extract_xml_id(self, element, xml_id: str, name: Optional[str],
                       line_number: int, model: str):
        """Extract generic XML ID."""
        self.items.append({
            'item_type': 'xml_id',
            'name': xml_id,
            'parent_name': None,
            'module': self.module_name,
            'attributes': {
                'model': model,
                'display_name': name or xml_id
            },
            'references': [{
                'file_path': self.relative_path,
                'line_number': line_number,
                'reference_type': 'definition',
                'context': xml_id
            }]
        })


def parse_xml_file(file_path: Path, module_name: str) -> list[dict]:
    """Parse an XML file and extract Odoo elements.

    Args:
        file_path: Path to XML file
        module_name: Odoo module name

    Returns:
        List of extracted items
    """
    parser = XMLParser(file_path, module_name)
    return parser.parse()
