# Wizard and Transient Model Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  WIZARD PATTERNS                                                             ║
║  Complete reference for transient models and wizard implementation           ║
║  Use for user interactions, batch operations, and confirmation dialogs       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Overview

Wizards (TransientModel) are temporary records that:
- Auto-delete after a period (vacuum)
- Don't persist permanently in database
- Perfect for user dialogs and batch operations
- Support multi-record operations

---

## Basic Wizard Structure

### Model Definition (v18)
```python
from odoo import api, fields, models
from odoo.exceptions import UserError


class MyWizard(models.TransientModel):
    _name = 'my.module.wizard'
    _description = 'My Wizard'

    # Context-dependent fields
    model_id = fields.Many2one(
        comodel_name='my.model',
        string='Record',
        default=lambda self: self.env.context.get('active_id'),
    )
    model_ids = fields.Many2many(
        comodel_name='my.model',
        string='Records',
        default=lambda self: self.env.context.get('active_ids'),
    )

    # Wizard-specific fields
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
    )
    note = fields.Text(string='Notes')

    def action_confirm(self) -> dict:
        """Execute wizard action."""
        self.ensure_one()

        if not self.model_id:
            raise UserError("No record selected.")

        # Perform operation
        self.model_id.write({
            'date': self.date,
            'notes': self.note,
        })

        return {'type': 'ir.actions.act_window_close'}
```

### View Definition
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="my_wizard_view_form" model="ir.ui.view">
        <field name="name">my.module.wizard.form</field>
        <field name="model">my.module.wizard</field>
        <field name="arch" type="xml">
            <form string="My Wizard">
                <group>
                    <field name="model_id" readonly="1"
                           invisible="not model_id"/>
                    <field name="date"/>
                    <field name="note"/>
                </group>
                <footer>
                    <button name="action_confirm"
                            string="Confirm"
                            type="object"
                            class="btn-primary"/>
                    <button string="Cancel"
                            class="btn-secondary"
                            special="cancel"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="my_wizard_action" model="ir.actions.act_window">
        <field name="name">My Wizard</field>
        <field name="res_model">my.module.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
        <field name="binding_model_id" ref="my_module.model_my_model"/>
        <field name="binding_view_types">form,list</field>
    </record>
</odoo>
```

### Security (ir.model.access.csv)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_wizard_user,my.module.wizard.user,model_my_module_wizard,base.group_user,1,1,1,1
```

---

## Common Wizard Patterns

### 1. Confirmation Dialog

```python
class ConfirmationWizard(models.TransientModel):
    _name = 'my.confirm.wizard'
    _description = 'Confirmation Dialog'

    message = fields.Text(
        string='Message',
        readonly=True,
        default=lambda self: self._default_message(),
    )

    @api.model
    def _default_message(self) -> str:
        active_ids = self.env.context.get('active_ids', [])
        count = len(active_ids)
        return f"Are you sure you want to process {count} record(s)?"

    def action_confirm(self) -> dict:
        """Process confirmed action."""
        active_ids = self.env.context.get('active_ids', [])
        records = self.env['my.model'].browse(active_ids)

        for record in records:
            record.action_process()

        return {'type': 'ir.actions.act_window_close'}
```

```xml
<form string="Confirm">
    <group>
        <field name="message" nolabel="1"/>
    </group>
    <footer>
        <button name="action_confirm" string="Yes, Proceed"
                type="object" class="btn-primary"/>
        <button string="Cancel" class="btn-secondary" special="cancel"/>
    </footer>
</form>
```

### 2. Batch Update Wizard

```python
class BatchUpdateWizard(models.TransientModel):
    _name = 'my.batch.update.wizard'
    _description = 'Batch Update'

    record_ids = fields.Many2many(
        comodel_name='my.model',
        string='Records to Update',
        default=lambda self: self._default_records(),
    )
    new_state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
        ],
        string='New Status',
        required=True,
    )
    update_date = fields.Boolean(
        string='Update Date',
        default=False,
    )
    date = fields.Date(
        string='New Date',
    )

    @api.model
    def _default_records(self) -> 'my.model':
        active_ids = self.env.context.get('active_ids', [])
        return self.env['my.model'].browse(active_ids)

    def action_update(self) -> dict:
        """Apply batch update."""
        vals = {'state': self.new_state}

        if self.update_date and self.date:
            vals['date'] = self.date

        self.record_ids.write(vals)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Updated {len(self.record_ids)} records.',
                'type': 'success',
                'sticky': False,
            }
        }
```

### 3. Report Wizard (Date Range)

```python
class ReportWizard(models.TransientModel):
    _name = 'my.report.wizard'
    _description = 'Report Parameters'

    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today,
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Partners',
        help='Leave empty for all partners',
    )
    output_format = fields.Selection(
        selection=[
            ('pdf', 'PDF'),
            ('xlsx', 'Excel'),
        ],
        string='Format',
        default='pdf',
        required=True,
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise UserError("Start date must be before end date.")

    def action_print(self) -> dict:
        """Generate report."""
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))

        records = self.env['my.model'].search(domain)

        if self.output_format == 'pdf':
            return self.env.ref('my_module.report_my_model').report_action(records)
        else:
            return self._export_xlsx(records)

    def _export_xlsx(self, records) -> dict:
        """Export to Excel."""
        # Implementation for Excel export
        pass
```

### 4. Import Wizard

```python
class ImportWizard(models.TransientModel):
    _name = 'my.import.wizard'
    _description = 'Import Data'

    file = fields.Binary(
        string='File',
        required=True,
        attachment=False,
    )
    filename = fields.Char(string='Filename')
    skip_errors = fields.Boolean(
        string='Skip Errors',
        default=False,
        help='Continue import even if some rows fail',
    )

    def action_import(self) -> dict:
        """Import data from file."""
        import base64
        import csv
        from io import StringIO

        if not self.file:
            raise UserError("Please select a file.")

        # Decode file
        file_content = base64.b64decode(self.file).decode('utf-8')
        reader = csv.DictReader(StringIO(file_content))

        created_count = 0
        error_count = 0
        errors = []

        for row_num, row in enumerate(reader, start=2):
            try:
                self._create_record(row)
                created_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Row {row_num}: {str(e)}")
                if not self.skip_errors:
                    raise UserError(f"Error on row {row_num}: {str(e)}")

        message = f"Created {created_count} records."
        if error_count:
            message += f" {error_count} errors."

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import Complete',
                'message': message,
                'type': 'success' if not error_count else 'warning',
            }
        }

    def _create_record(self, row: dict) -> 'my.model':
        """Create record from row data."""
        return self.env['my.model'].create({
            'name': row['name'],
            'code': row.get('code'),
        })
```

### 5. Selection Wizard (Multi-step)

```python
class SelectionWizard(models.TransientModel):
    _name = 'my.selection.wizard'
    _description = 'Selection Wizard'

    step = fields.Selection(
        selection=[
            ('select', 'Selection'),
            ('configure', 'Configuration'),
            ('confirm', 'Confirmation'),
        ],
        string='Step',
        default='select',
    )

    # Step 1: Selection
    template_id = fields.Many2one(
        comodel_name='my.template',
        string='Template',
    )

    # Step 2: Configuration
    name = fields.Char(string='Name')
    date = fields.Date(string='Date')

    # Step 3: Confirmation
    summary = fields.Text(
        string='Summary',
        compute='_compute_summary',
    )

    @api.depends('template_id', 'name', 'date')
    def _compute_summary(self):
        for wizard in self:
            wizard.summary = f"""
Template: {wizard.template_id.name or 'None'}
Name: {wizard.name or 'Not set'}
Date: {wizard.date or 'Not set'}
            """

    def action_next(self) -> dict:
        """Go to next step."""
        self.ensure_one()

        if self.step == 'select':
            if not self.template_id:
                raise UserError("Please select a template.")
            self.step = 'configure'
        elif self.step == 'configure':
            if not self.name:
                raise UserError("Please enter a name.")
            self.step = 'confirm'

        return self._reopen()

    def action_previous(self) -> dict:
        """Go to previous step."""
        self.ensure_one()

        if self.step == 'configure':
            self.step = 'select'
        elif self.step == 'confirm':
            self.step = 'configure'

        return self._reopen()

    def action_create(self) -> dict:
        """Create record from wizard."""
        self.ensure_one()

        record = self.env['my.model'].create({
            'template_id': self.template_id.id,
            'name': self.name,
            'date': self.date,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'my.model',
            'res_id': record.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _reopen(self) -> dict:
        """Reopen wizard at current state."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
```

---

## Wizard Action Return Types

### Close Wizard
```python
return {'type': 'ir.actions.act_window_close'}
```

### Notification
```python
return {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Success',
        'message': 'Operation completed.',
        'type': 'success',  # success, warning, danger, info
        'sticky': False,
    }
}
```

### Open Record
```python
return {
    'type': 'ir.actions.act_window',
    'res_model': 'my.model',
    'res_id': record_id,
    'view_mode': 'form',
    'target': 'current',  # current, new, inline
}
```

### Open List
```python
return {
    'type': 'ir.actions.act_window',
    'name': 'Created Records',
    'res_model': 'my.model',
    'view_mode': 'tree,form',
    'domain': [('id', 'in', record_ids)],
    'target': 'current',
}
```

### Download Report
```python
return self.env.ref('my_module.report_action').report_action(records)
```

### Reload Page
```python
return {
    'type': 'ir.actions.client',
    'tag': 'reload',
}
```

---

## Binding to Models

### From Action Definition
```xml
<record id="my_wizard_action" model="ir.actions.act_window">
    <field name="name">My Wizard</field>
    <field name="res_model">my.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
    <!-- Bind to specific model's Action menu -->
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_view_types">form,list</field>
</record>
```

### From Python (Server Action)
```python
def action_open_wizard(self) -> dict:
    """Open wizard from button."""
    return {
        'type': 'ir.actions.act_window',
        'name': 'My Wizard',
        'res_model': 'my.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_model_id': self.id,
            'default_model_ids': self.ids,
            'active_id': self.id,
            'active_ids': self.ids,
            'active_model': self._name,
        },
    }
```

---

## Version-Specific Notes

### v17+ View Syntax
```xml
<!-- Use inline expressions -->
<field name="date" invisible="not update_date"/>
<button name="action_next" invisible="step == 'confirm'"/>
```

### v18+ Type Hints
```python
def action_confirm(self) -> dict:
    """Execute with type hints."""
    self.ensure_one()
    return {'type': 'ir.actions.act_window_close'}

@api.model
def _default_records(self) -> 'my.model':
    return self.env['my.model'].browse(
        self.env.context.get('active_ids', [])
    )
```

---

## Best Practices

1. **Always define security** - Wizards need ir.model.access.csv entries
2. **Use context defaults** - Pass active_id/active_ids through context
3. **Validate input** - Use @api.constrains and raise UserError
4. **Handle empty selection** - Check if records exist before processing
5. **Provide feedback** - Return notification or open result view
6. **Clean UI** - Use footer for buttons, proper grouping
7. **Multi-record support** - Use Many2many for batch operations
