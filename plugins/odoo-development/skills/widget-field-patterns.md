# Widget and Field Rendering Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  WIDGET & FIELD RENDERING PATTERNS                                           ║
║  Field widgets, custom rendering, and UI components                          ║
║  Use for customizing field display in forms, trees, and kanban views         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Common Widgets Reference

### Text and Selection Widgets
| Widget | Field Types | Description |
|--------|-------------|-------------|
| `char` | Char | Default text input |
| `text` | Text | Multiline textarea |
| `html` | Html | Rich text editor |
| `email` | Char | Email with mailto link |
| `url` | Char | URL with clickable link |
| `phone` | Char | Phone with tel: link |
| `selection` | Selection | Dropdown select |
| `radio` | Selection | Radio buttons |
| `badge` | Selection | Colored badge display |
| `statusbar` | Selection | Status bar progression |

### Numeric Widgets
| Widget | Field Types | Description |
|--------|-------------|-------------|
| `integer` | Integer | Default integer |
| `float` | Float | Default decimal |
| `monetary` | Float/Monetary | Currency formatted |
| `percentage` | Float | Percentage display |
| `progressbar` | Float/Integer | Progress bar |
| `float_time` | Float | Hours:minutes format |
| `handle` | Integer | Drag handle for reordering |

### Date and Time Widgets
| Widget | Field Types | Description |
|--------|-------------|-------------|
| `date` | Date | Date picker |
| `datetime` | Datetime | Date and time picker |
| `daterange` | Date | Date range picker |
| `remaining_days` | Date | Days remaining display |

### Relational Widgets
| Widget | Field Types | Description |
|--------|-------------|-------------|
| `many2one` | Many2one | Default dropdown |
| `many2one_avatar` | Many2one | With avatar image |
| `many2one_avatar_user` | Many2one | User with avatar |
| `many2one_avatar_employee` | Many2one | Employee with avatar |
| `many2many_tags` | Many2many | Tag pills |
| `many2many_tags_avatar` | Many2many | Tags with avatars |
| `many2many_checkboxes` | Many2many | Checkbox list |
| `one2many` | One2many | Inline list/table |
| `section_and_note_one2many` | One2many | With sections (sale lines) |

### Binary Widgets
| Widget | Field Types | Description |
|--------|-------------|-------------|
| `binary` | Binary | File upload |
| `image` | Binary | Image display/upload |
| `signature` | Binary | Signature pad |
| `pdf_viewer` | Binary | PDF inline viewer |

### Special Widgets
| Widget | Field Types | Description |
|--------|-------------|-------------|
| `boolean_toggle` | Boolean | Toggle switch |
| `boolean_favorite` | Boolean | Star icon |
| `priority` | Selection | Star priority |
| `color_picker` | Integer | Color selection |
| `domain` | Char | Domain builder |
| `ace` | Text | Code editor |
| `copy_clipboard_char` | Char | Copy button |
| `copy_clipboard_text` | Text | Copy button |

---

## Widget Usage in Views

### Form View Widgets
```xml
<form>
    <sheet>
        <group>
            <!-- Text widgets -->
            <field name="name"/>
            <field name="email" widget="email"/>
            <field name="website" widget="url"/>
            <field name="phone" widget="phone"/>
            <field name="description" widget="html"/>

            <!-- Selection widgets -->
            <field name="type" widget="radio"/>
            <field name="priority" widget="priority"/>
            <field name="state" widget="badge"/>

            <!-- Numeric widgets -->
            <field name="amount" widget="monetary"/>
            <field name="discount" widget="percentage"/>
            <field name="progress" widget="progressbar"/>
            <field name="duration" widget="float_time"/>

            <!-- Date widgets -->
            <field name="date_deadline" widget="remaining_days"/>

            <!-- Relational widgets -->
            <field name="user_id" widget="many2one_avatar_user"/>
            <field name="tag_ids" widget="many2many_tags"/>
            <field name="category_ids" widget="many2many_checkboxes"/>

            <!-- Binary widgets -->
            <field name="image" widget="image"/>
            <field name="signature" widget="signature"/>
            <field name="document" widget="binary"/>

            <!-- Special widgets -->
            <field name="is_favorite" widget="boolean_favorite" nolabel="1"/>
            <field name="active" widget="boolean_toggle"/>
            <field name="color" widget="color_picker"/>
        </group>
    </sheet>
</form>
```

### Tree View Widgets
```xml
<tree>
    <!-- Handle for drag-drop reordering -->
    <field name="sequence" widget="handle"/>

    <field name="name"/>
    <field name="state" widget="badge" decoration-success="state == 'done'"
           decoration-warning="state == 'pending'"
           decoration-danger="state == 'cancel'"/>
    <field name="amount" widget="monetary"/>
    <field name="progress" widget="progressbar"/>
    <field name="user_id" widget="many2one_avatar_user"/>
    <field name="tag_ids" widget="many2many_tags"/>
    <field name="is_favorite" widget="boolean_favorite" nolabel="1"/>
</tree>
```

### Kanban View Widgets
```xml
<kanban>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <!-- Avatar widget in kanban -->
                <field name="user_id" widget="many2one_avatar_user"/>

                <!-- Priority stars -->
                <field name="priority" widget="priority"/>

                <!-- Progress bar -->
                <field name="progress" widget="progressbar"/>

                <!-- Tags -->
                <field name="tag_ids" widget="many2many_tags"
                       options="{'color_field': 'color'}"/>
            </div>
        </t>
    </templates>
</kanban>
```

---

## Widget Options

### Many2one Options
```xml
<!-- No create option -->
<field name="partner_id" options="{'no_create': True}"/>

<!-- No create, no edit, no open -->
<field name="partner_id" options="{
    'no_create': True,
    'no_create_edit': True,
    'no_open': True
}"/>

<!-- Custom create label -->
<field name="partner_id" options="{'create_name_field': 'display_name'}"/>
```

### Many2many Tags Options
```xml
<!-- With color -->
<field name="tag_ids" widget="many2many_tags"
       options="{'color_field': 'color'}"/>

<!-- No create, limited -->
<field name="tag_ids" widget="many2many_tags"
       options="{'no_create': True, 'limit': 5}"/>
```

### Monetary Options
```xml
<!-- Specify currency field -->
<field name="amount" widget="monetary"
       options="{'currency_field': 'currency_id'}"/>
```

### Image Options
```xml
<!-- With size and preview -->
<field name="image" widget="image"
       options="{'size': [128, 128], 'preview_image': 'image_128'}"/>

<!-- Zoom on click -->
<field name="image" widget="image" options="{'zoom': true}"/>
```

### Progressbar Options
```xml
<!-- With current/max values -->
<field name="progress" widget="progressbar"
       options="{'current_value': 'done_count', 'max_value': 'total_count'}"/>

<!-- Editable -->
<field name="progress" widget="progressbar"
       options="{'editable': true}"/>
```

### Statusbar Options
```xml
<!-- Visible states -->
<field name="state" widget="statusbar"
       statusbar_visible="draft,confirmed,done"/>

<!-- Clickable states -->
<field name="state" widget="statusbar"
       options="{'clickable': '1'}"/>
```

---

## Field Decorations

### Tree View Decorations
```xml
<tree decoration-success="state == 'done'"
      decoration-warning="state == 'pending'"
      decoration-danger="state == 'cancel'"
      decoration-info="state == 'draft'"
      decoration-muted="not active"
      decoration-bf="is_important">
    <field name="name"/>
    <field name="state"/>
    <field name="active" column_invisible="True"/>
    <field name="is_important" column_invisible="True"/>
</tree>
```

### Available Decorations
| Decoration | Style |
|------------|-------|
| `decoration-bf` | Bold |
| `decoration-it` | Italic |
| `decoration-success` | Green |
| `decoration-info` | Blue |
| `decoration-warning` | Orange |
| `decoration-danger` | Red |
| `decoration-muted` | Gray |
| `decoration-primary` | Primary color |
| `decoration-secondary` | Secondary color |

---

## Conditional Widget Display

### Readonly Conditions
```xml
<!-- Readonly based on state -->
<field name="amount" readonly="state != 'draft'"/>

<!-- Readonly based on field value -->
<field name="partner_id" readonly="is_locked"/>
```

### Invisible Conditions
```xml
<!-- Hide based on type -->
<field name="product_id" invisible="type != 'product'"/>

<!-- Hide based on state -->
<field name="cancel_reason" invisible="state != 'cancel'"/>
```

### Required Conditions
```xml
<!-- Required based on type -->
<field name="partner_id" required="type == 'customer'"/>

<!-- Required based on state -->
<field name="date_done" required="state == 'done'"/>
```

---

## Special Field Patterns

### Statusbar with Buttons
```xml
<header>
    <button name="action_confirm" string="Confirm"
            type="object" invisible="state != 'draft'"
            class="oe_highlight"/>
    <button name="action_done" string="Done"
            type="object" invisible="state != 'confirmed'"
            class="oe_highlight"/>
    <button name="action_cancel" string="Cancel"
            type="object" invisible="state in ['done', 'cancel']"/>
    <field name="state" widget="statusbar"
           statusbar_visible="draft,confirmed,done"/>
</header>
```

### Priority Stars
```xml
<!-- Model definition -->
priority = fields.Selection([
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'High'),
    ('3', 'Very High'),
], default='0')

<!-- In view -->
<field name="priority" widget="priority"/>
```

### Favorite Star
```xml
<!-- Model definition -->
is_favorite = fields.Boolean(default=False)

<!-- In view -->
<field name="is_favorite" widget="boolean_favorite" nolabel="1"/>
```

### Color Picker
```xml
<!-- Model definition -->
color = fields.Integer(string='Color Index')

<!-- In view -->
<field name="color" widget="color_picker"/>
```

### Handle for Reordering
```xml
<!-- Model definition -->
sequence = fields.Integer(default=10)

<!-- In tree view -->
<tree>
    <field name="sequence" widget="handle"/>
    <field name="name"/>
</tree>
```

---

## Badge Decorations

### State Badge
```xml
<!-- Selection field -->
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
], default='draft')

<!-- In view with colors -->
<field name="state" widget="badge"
       decoration-success="state == 'done'"
       decoration-info="state == 'draft'"
       decoration-warning="state == 'confirmed'"
       decoration-danger="state == 'cancel'"/>
```

### Type Badge
```xml
<field name="type" widget="badge"
       decoration-primary="type == 'product'"
       decoration-secondary="type == 'service'"/>
```

---

## Monetary Field Pattern

### Complete Setup
```python
# Model definition
class MyModel(models.Model):
    _name = 'my.model'

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    amount = fields.Monetary(currency_field='currency_id')
    amount_untaxed = fields.Monetary(currency_field='currency_id')
    amount_tax = fields.Monetary(currency_field='currency_id')
    amount_total = fields.Monetary(
        currency_field='currency_id',
        compute='_compute_amount_total',
        store=True,
    )

    @api.depends('amount_untaxed', 'amount_tax')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.amount_untaxed + record.amount_tax
```

```xml
<!-- View -->
<group>
    <field name="currency_id" groups="base.group_multi_currency"/>
    <field name="amount_untaxed"/>
    <field name="amount_tax"/>
    <field name="amount_total"/>
</group>
```

---

## Version-Specific Notes

### Odoo 17+ (visibility attributes)
```xml
<!-- New syntax -->
<field name="field1" invisible="condition"/>
<field name="field2" readonly="condition"/>
<field name="field3" required="condition"/>
<field name="field4" column_invisible="condition"/>
```

### Odoo 14-16 (attrs)
```xml
<!-- Old syntax -->
<field name="field1" attrs="{'invisible': [('condition', '=', True)]}"/>
<field name="field2" attrs="{'readonly': [('state', '!=', 'draft')]}"/>
<field name="field3" attrs="{'required': [('type', '=', 'customer')]}"/>
```

---

## Best Practices

1. **Use appropriate widgets** - Match widget to data type and UX need
2. **Set widget options** - Configure behavior with options dict
3. **Use decorations** - Visual cues for states and priorities
4. **Handle currency** - Always specify currency_field for monetary
5. **Use avatar widgets** - Better UX for user/partner fields
6. **Status progression** - Use statusbar for state workflows
7. **Drag reordering** - Add handle widget for sequences
8. **Tags with colors** - Use color_field option for tags
9. **Conditional display** - Use invisible/readonly/required
10. **Version awareness** - attrs vs direct attributes
