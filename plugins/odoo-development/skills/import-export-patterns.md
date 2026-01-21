# Import/Export Data Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  IMPORT/EXPORT DATA PATTERNS                                                 ║
║  CSV import, Excel export, data migration, and bulk operations               ║
║  Use for data loading, reporting exports, and system integration             ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## CSV Import Basics

### Standard Import Format
```csv
id,name,email,phone,country_id/id
partner_001,Acme Corp,info@acme.com,+1-555-0100,base.us
partner_002,Beta Inc,contact@beta.com,+1-555-0200,base.us
__import__.partner_003,Gamma LLC,hello@gamma.com,+1-555-0300,base.ca
```

### Import Column Patterns
| Pattern | Description | Example |
|---------|-------------|---------|
| `field` | Direct field | `name`, `email` |
| `field/id` | External ID reference | `country_id/id` |
| `field.subfield` | Related field | `partner_id.name` |
| `field/0/subfield` | One2many line | `line_ids/0/product_id` |

---

## Programmatic Import

### Import CSV Data
```python
import base64
import csv
from io import StringIO


def import_partners_from_csv(self, csv_content):
    """Import partners from CSV string."""
    reader = csv.DictReader(StringIO(csv_content))

    created = []
    errors = []

    for row in reader:
        try:
            # Find country by code
            country = self.env['res.country'].search([
                ('code', '=', row.get('country_code', 'US'))
            ], limit=1)

            partner = self.env['res.partner'].create({
                'name': row['name'],
                'email': row.get('email'),
                'phone': row.get('phone'),
                'country_id': country.id,
            })
            created.append(partner.id)
        except Exception as e:
            errors.append({
                'row': row,
                'error': str(e),
            })

    return {
        'created': created,
        'errors': errors,
        'total': len(created) + len(errors),
    }
```

### Using base_import
```python
def import_with_base_import(self, model_name, csv_content, fields):
    """Use Odoo's base import functionality."""
    import_wizard = self.env['base_import.import'].create({
        'res_model': model_name,
        'file': base64.b64encode(csv_content.encode()),
        'file_name': 'import.csv',
        'file_type': 'text/csv',
    })

    result = import_wizard.execute_import(
        fields,  # ['name', 'email', 'country_id/id']
        [],  # columns (auto-detect)
        {'quoting': '"', 'separator': ',', 'headers': True}
    )

    return result
```

---

## Export Data

### Export to CSV
```python
import csv
from io import StringIO
import base64


def export_partners_to_csv(self, domain=None):
    """Export partners to CSV."""
    partners = self.env['res.partner'].search(domain or [])

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Country'])

    # Data
    for partner in partners:
        writer.writerow([
            partner.id,
            partner.name,
            partner.email or '',
            partner.phone or '',
            partner.country_id.name or '',
        ])

    content = output.getvalue()
    output.close()

    return content
```

### Export to Excel
```python
import xlsxwriter
from io import BytesIO
import base64


def export_to_excel(self, records, fields, filename='export.xlsx'):
    """Export records to Excel file."""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Data')

    # Styles
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'border': 1,
    })
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    money_format = workbook.add_format({'num_format': '#,##0.00'})

    # Write header
    for col, field in enumerate(fields):
        worksheet.write(0, col, field, header_format)

    # Write data
    for row, record in enumerate(records, start=1):
        for col, field in enumerate(fields):
            value = record[field]
            if isinstance(value, (int, float)):
                worksheet.write_number(row, col, value)
            elif hasattr(value, 'id'):  # Many2one
                worksheet.write(row, col, value.display_name or '')
            else:
                worksheet.write(row, col, str(value) if value else '')

    workbook.close()
    output.seek(0)

    return base64.b64encode(output.read())
```

---

## Import Wizard

### Create Import Wizard
```python
class ImportWizard(models.TransientModel):
    _name = 'import.wizard'
    _description = 'Import Wizard'

    file = fields.Binary(string='File', required=True)
    file_name = fields.Char(string='File Name')
    import_type = fields.Selection([
        ('create', 'Create Only'),
        ('update', 'Update Only'),
        ('create_update', 'Create or Update'),
    ], default='create', required=True)

    result_ids = fields.One2many(
        'import.wizard.result',
        'wizard_id',
        string='Results',
    )

    def action_import(self):
        """Process the import."""
        self.ensure_one()

        # Decode file
        content = base64.b64decode(self.file).decode('utf-8')
        reader = csv.DictReader(StringIO(content))

        results = []
        for row_num, row in enumerate(reader, start=2):
            try:
                record = self._process_row(row)
                results.append({
                    'wizard_id': self.id,
                    'row_number': row_num,
                    'status': 'success',
                    'record_id': record.id,
                    'message': f'Created: {record.display_name}',
                })
            except Exception as e:
                results.append({
                    'wizard_id': self.id,
                    'row_number': row_num,
                    'status': 'error',
                    'message': str(e),
                })

        self.env['import.wizard.result'].create(results)

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _process_row(self, row):
        """Process single row. Override in subclass."""
        raise NotImplementedError()


class ImportWizardResult(models.TransientModel):
    _name = 'import.wizard.result'
    _description = 'Import Result'

    wizard_id = fields.Many2one('import.wizard')
    row_number = fields.Integer()
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'),
        ('skipped', 'Skipped'),
    ])
    record_id = fields.Integer()
    message = fields.Char()
```

### Wizard View
```xml
<record id="import_wizard_form" model="ir.ui.view">
    <field name="name">import.wizard.form</field>
    <field name="model">import.wizard</field>
    <field name="arch" type="xml">
        <form>
            <group invisible="result_ids">
                <field name="file" filename="file_name"/>
                <field name="file_name" invisible="1"/>
                <field name="import_type"/>
            </group>
            <group string="Results" invisible="not result_ids">
                <field name="result_ids" nolabel="1">
                    <tree>
                        <field name="row_number"/>
                        <field name="status" decoration-success="status == 'success'"
                               decoration-danger="status == 'error'"/>
                        <field name="message"/>
                    </tree>
                </field>
            </group>
            <footer>
                <button name="action_import" string="Import" type="object"
                        class="btn-primary" invisible="result_ids"/>
                <button string="Close" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

---

## External ID Handling

### Create with External ID
```python
def import_with_xmlid(self, model, xmlid, vals):
    """Create/update record with external ID."""
    # Check if record exists
    record = self.env.ref(xmlid, raise_if_not_found=False)

    if record:
        record.write(vals)
    else:
        # Create with external ID
        record = self.env[model].create(vals)

        # Create external ID
        module, name = xmlid.split('.')
        self.env['ir.model.data'].create({
            'name': name,
            'module': module,
            'model': model,
            'res_id': record.id,
            'noupdate': False,
        })

    return record
```

### Lookup by External ID
```python
def get_by_xmlid(self, xmlid, model=None):
    """Get record by external ID."""
    record = self.env.ref(xmlid, raise_if_not_found=False)
    if record and model:
        if record._name != model:
            return None
    return record

def get_xmlid(self, record):
    """Get external ID for record."""
    data = self.env['ir.model.data'].search([
        ('model', '=', record._name),
        ('res_id', '=', record.id),
    ], limit=1)
    return f'{data.module}.{data.name}' if data else None
```

---

## Batch Processing

### Import Large Files
```python
def import_large_file(self, file_path, batch_size=1000):
    """Import large file in batches."""
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        batch = []
        total_created = 0

        for row in reader:
            batch.append(self._prepare_vals(row))

            if len(batch) >= batch_size:
                self.env['my.model'].create(batch)
                total_created += len(batch)
                batch = []
                self.env.cr.commit()  # Commit batch

        # Process remaining
        if batch:
            self.env['my.model'].create(batch)
            total_created += len(batch)
            self.env.cr.commit()

    return total_created
```

### Background Import
```python
def action_import_async(self):
    """Queue import for background processing."""
    self.ensure_one()

    # Create attachment for the file
    attachment = self.env['ir.attachment'].create({
        'name': self.file_name,
        'datas': self.file,
        'res_model': self._name,
        'res_id': self.id,
    })

    # Schedule cron job or use queue_job
    self.env['ir.cron'].create({
        'name': f'Import: {self.file_name}',
        'model_id': self.env.ref('my_module.model_import_wizard').id,
        'state': 'code',
        'code': f'model.browse({self.id})._process_import_async()',
        'interval_number': 1,
        'interval_type': 'minutes',
        'numbercall': 1,
        'doall': True,
    })

    return {'type': 'ir.actions.client', 'tag': 'reload'}
```

---

## Export Reports

### Excel Report with Multiple Sheets
```python
def export_report_excel(self):
    """Export multi-sheet Excel report."""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    # Summary sheet
    summary = workbook.add_worksheet('Summary')
    summary.write(0, 0, 'Total Records')
    summary.write(0, 1, self.search_count([]))

    # Detail sheet
    detail = workbook.add_worksheet('Details')
    records = self.search([])

    # Headers
    headers = ['ID', 'Name', 'Date', 'Amount']
    for col, header in enumerate(headers):
        detail.write(0, col, header)

    # Data
    for row, rec in enumerate(records, start=1):
        detail.write(row, 0, rec.id)
        detail.write(row, 1, rec.name)
        detail.write(row, 2, str(rec.date) if rec.date else '')
        detail.write(row, 3, rec.amount)

    workbook.close()
    output.seek(0)

    # Create attachment
    attachment = self.env['ir.attachment'].create({
        'name': 'report.xlsx',
        'datas': base64.b64encode(output.read()),
        'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })

    return {
        'type': 'ir.actions.act_url',
        'url': f'/web/content/{attachment.id}?download=true',
        'target': 'self',
    }
```

---

## JSON Import/Export

### Export to JSON
```python
import json


def export_to_json(self, records, fields):
    """Export records to JSON."""
    data = []
    for record in records:
        row = {}
        for field in fields:
            value = record[field]
            if hasattr(value, 'id'):  # Relational
                row[field] = {'id': value.id, 'name': value.display_name}
            elif hasattr(value, 'ids'):  # X2many
                row[field] = [{'id': r.id, 'name': r.display_name} for r in value]
            elif isinstance(value, (date, datetime)):
                row[field] = value.isoformat()
            else:
                row[field] = value
        data.append(row)

    return json.dumps(data, indent=2, default=str)
```

### Import from JSON
```python
def import_from_json(self, json_content):
    """Import records from JSON."""
    data = json.loads(json_content)

    created = []
    for row in data:
        # Process relational fields
        vals = {}
        for key, value in row.items():
            if isinstance(value, dict) and 'id' in value:
                vals[key] = value['id']
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                vals[key] = [(6, 0, [v['id'] for v in value])]
            else:
                vals[key] = value

        record = self.create(vals)
        created.append(record.id)

    return created
```

---

## Data Validation

### Validate Import Data
```python
def validate_import_row(self, row):
    """Validate a single import row."""
    errors = []

    # Required fields
    if not row.get('name'):
        errors.append('Name is required')

    # Email format
    if row.get('email'):
        import re
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', row['email']):
            errors.append(f"Invalid email: {row['email']}")

    # Reference lookup
    if row.get('country_code'):
        country = self.env['res.country'].search([
            ('code', '=', row['country_code'])
        ], limit=1)
        if not country:
            errors.append(f"Unknown country: {row['country_code']}")

    return errors
```

---

## Best Practices

1. **Validate first** - Check all rows before creating any
2. **Use transactions** - Rollback on errors
3. **Batch processing** - Commit in chunks for large imports
4. **External IDs** - Use for data that may be re-imported
5. **Error reporting** - Show row numbers and specific errors
6. **Preview mode** - Let users review before committing
7. **Template download** - Provide import template
8. **Encoding** - Handle UTF-8 properly
9. **Progress feedback** - Show import progress
10. **Logging** - Log imports for audit trail
