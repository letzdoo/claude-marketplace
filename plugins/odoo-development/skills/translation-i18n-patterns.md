# Translation and Internationalization Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  TRANSLATION & I18N PATTERNS                                                 ║
║  Multi-language support, translations, and localization                      ║
║  Use for modules that need to support multiple languages                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Translation Basics

### Translatable Strings in Python
```python
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'  # Translatable

    # Field labels are translatable by default
    name = fields.Char(string='Name', required=True)

    # Help text is translatable
    description = fields.Text(
        string='Description',
        help='Enter a detailed description',  # Translatable
    )

    # Selection labels are translatable
    state = fields.Selection([
        ('draft', 'Draft'),      # 'Draft' is translatable
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string='Status', default='draft')

    def action_confirm(self):
        """Use _() for translatable messages."""
        for record in self:
            if not record.name:
                # Translatable error message
                raise UserError(_("Name is required to confirm."))

            record.state = 'confirmed'
            # Translatable success message
            record.message_post(body=_("Document confirmed."))
```

### Translation Function Patterns
```python
from odoo import _

# Simple translation
message = _("This is a translatable string")

# Translation with formatting (use %s or .format())
name = "Test"
message = _("Record %s has been created") % name

# Translation with multiple values
message = _("Created %s records in %s seconds") % (count, time)

# Translation with named placeholders (Python 3.6+)
message = _("Record %(name)s created by %(user)s") % {
    'name': record.name,
    'user': self.env.user.name,
}

# DO NOT use f-strings for translatable text!
# Bad: _(f"Record {name} created")  # Won't be extracted!
# Good: _("Record %s created") % name
```

---

## Translatable Field Content

### Translated Fields
```python
class Product(models.Model):
    _name = 'product.product'

    # translate=True makes field content translatable per language
    name = fields.Char(string='Name', translate=True)
    description = fields.Text(string='Description', translate=True)

    # Html fields can also be translatable
    website_description = fields.Html(
        string='Website Description',
        translate=True,
    )
```

### Reading Translated Values
```python
def get_translated_name(self):
    """Get field value in specific language."""
    # Current user's language
    name = self.name

    # Specific language
    name_fr = self.with_context(lang='fr_FR').name
    name_de = self.with_context(lang='de_DE').name

    return {
        'current': name,
        'french': name_fr,
        'german': name_de,
    }

def set_translated_value(self, field, value, lang):
    """Set field value for specific language."""
    self.with_context(lang=lang).write({field: value})
```

---

## XML Translations

### Translatable View Elements
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="my_model_view_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <!-- Button strings are translatable -->
                    <button name="action_confirm" string="Confirm"
                            type="object" class="oe_highlight"/>
                </header>
                <sheet>
                    <group>
                        <!-- Field labels from model definition -->
                        <field name="name"/>
                    </group>
                    <group string="Additional Info">
                        <!-- Group title is translatable -->
                        <field name="description"
                               placeholder="Enter description..."/>
                        <!-- Placeholder is translatable -->
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Menu items are translatable -->
    <menuitem id="menu_my_model"
              name="My Records"
              action="action_my_model"/>
</odoo>
```

### Translatable Data Records
```xml
<!-- Static data with translations -->
<record id="my_category_electronics" model="my.category">
    <field name="name">Electronics</field>  <!-- Translatable -->
    <field name="description">Electronic devices and components</field>
</record>

<!-- Email template -->
<record id="email_template_confirmation" model="mail.template">
    <field name="name">Confirmation Email</field>
    <field name="subject">Order {{ object.name }} Confirmed</field>
    <field name="body_html"><![CDATA[
        <p>Dear {{ object.partner_id.name }},</p>
        <p>Your order has been confirmed.</p>
    ]]></field>
</record>
```

---

## PO File Structure

### Translation File Location
```
my_module/
├── i18n/
│   ├── my_module.pot      # Template (source)
│   ├── fr.po              # French
│   ├── de.po              # German
│   ├── es.po              # Spanish
│   ├── fr_CA.po           # French (Canada)
│   └── pt_BR.po           # Portuguese (Brazil)
```

### PO File Format
```po
# Translation for Odoo module my_module
# French translation
msgid ""
msgstr ""
"Project-Id-Version: Odoo 17.0\n"
"Language: fr\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

#. module: my_module
#: model:ir.model,name:my_module.model_my_model
msgid "My Model"
msgstr "Mon Modèle"

#. module: my_module
#: model:ir.model.fields,field_description:my_module.field_my_model__name
msgid "Name"
msgstr "Nom"

#. module: my_module
#: code:addons/my_module/models/my_model.py:0
#, python-format
msgid "Record %s has been created"
msgstr "L'enregistrement %s a été créé"

#. module: my_module
#: model_terms:ir.ui.view,arch_db:my_module.my_model_view_form
msgid "Confirm"
msgstr "Confirmer"
```

---

## Generating Translations

### Export POT Template
```bash
# From Odoo directory
./odoo-bin -d mydb --i18n-export=/tmp/my_module.pot --modules=my_module

# Or using odoo shell
odoo shell -d mydb
>>> self.env['ir.translation'].export_terms_url('my_module', 'pot')
```

### Programmatic Translation Export
```python
def action_export_translations(self):
    """Export module translations."""
    module = self.env['ir.module.module'].search([
        ('name', '=', 'my_module'),
    ])

    # Export to POT
    translations = self.env['base.language.export'].create({
        'format': 'po',
        'modules': [(6, 0, [module.id])],
    })
    translations.act_getfile()
```

---

## Language Installation

### Install Language from Code
```python
def install_language(self, lang_code):
    """Install a language."""
    lang = self.env['res.lang']._activate_lang(lang_code)
    if lang:
        # Load translations
        self.env['ir.module.module']._load_module_terms(
            ['my_module'], [lang_code]
        )
    return lang
```

### Check Available Languages
```python
def get_available_languages(self):
    """Get list of active languages."""
    return self.env['res.lang'].search([('active', '=', True)])

def get_user_language(self):
    """Get current user's language."""
    return self.env.user.lang or self.env.context.get('lang', 'en_US')
```

---

## Context-Based Language

### Switch Language in Code
```python
def process_in_language(self, lang_code):
    """Execute code in specific language context."""
    # Method 1: with_context
    records_fr = self.with_context(lang='fr_FR')
    name_fr = records_fr.name

    # Method 2: sudo with language
    partner = self.env['res.partner'].with_context(lang='de_DE').browse(1)
    german_name = partner.name

def send_email_in_partner_language(self):
    """Send email in partner's language."""
    for record in self:
        partner = record.partner_id
        lang = partner.lang or 'en_US'

        # Render template in partner's language
        template = self.env.ref('my_module.email_template')
        template.with_context(lang=lang).send_mail(record.id)
```

---

## Report Translations

### QWeb Report with Translations
```xml
<template id="report_my_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <!-- Translatable text -->
                    <h1>Order Confirmation</h1>

                    <table>
                        <thead>
                            <tr>
                                <!-- Column headers translatable -->
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="doc.line_ids" t-as="line">
                                <tr>
                                    <!-- Product name in document language -->
                                    <td t-esc="line.product_id.with_context(lang=doc.partner_id.lang).name"/>
                                    <td t-esc="line.quantity"/>
                                    <td t-field="line.price_unit"/>
                                </tr>
                            </t>
                        </tbody>
                    </table>

                    <!-- Translated footer -->
                    <p>Thank you for your order!</p>
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Dynamic Translation

### Translate at Runtime
```python
def get_translated_status(self):
    """Get translated selection value."""
    # Get the translated label for current selection value
    selection = self._fields['state'].selection
    if callable(selection):
        selection = selection(self)

    return dict(selection).get(self.state, self.state)

def translate_text(self, text, lang=None):
    """Translate arbitrary text."""
    if lang:
        self = self.with_context(lang=lang)

    # Use _() for registered translations
    return _(text)
```

---

## Translation Best Practices

### Do's and Don'ts
```python
# GOOD: Use _() for user-facing strings
raise UserError(_("Cannot delete confirmed record."))

# GOOD: Separate translatable and non-translatable
_logger.info("Record %s processed", record.id)  # Log: not translated
record.message_post(body=_("Record processed."))  # UI: translated

# GOOD: Keep format specifiers outside translation
_("Total: %s items") % count

# BAD: f-strings break translation extraction
_(f"Total: {count} items")  # Won't be extracted!

# BAD: Concatenation breaks translation
_("Hello ") + name + _("!")  # Split translations

# GOOD: Use single translatable string
_("Hello %s!") % name

# BAD: HTML in translation
_("<b>Important:</b> Please confirm")  # Hard to translate

# GOOD: Separate HTML from text
"<b>%s</b>" % _("Important: Please confirm")
```

### Sentence Context
```python
# BAD: Ambiguous word
_("Order")  # Noun or verb?

# GOOD: Provide context with full sentence
_("Sales Order")  # Clear it's a noun
_("Order by date")  # Clear it's a verb

# GOOD: Use comments for translators
# Translators: This is a button label for creating new record
_("New")
```

---

## Selection Field Translations

### Proper Selection Pattern
```python
class MyModel(models.Model):
    _name = 'my.model'

    # Selection values are extracted for translation
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', default='1')

    # Dynamic selection (still translatable)
    @api.model
    def _get_type_selection(self):
        return [
            ('type_a', _('Type A')),  # Use _() for dynamic
            ('type_b', _('Type B')),
        ]

    type = fields.Selection(
        selection='_get_type_selection',
        string='Type',
    )
```

---

## Multi-Language Website

### Website Content Translation
```python
class WebsitePage(models.Model):
    _inherit = 'website.page'

    # Content translatable per language
    content = fields.Html(translate=True)
```

### Controller with Language
```python
from odoo import http
from odoo.http import request


class MyController(http.Controller):

    @http.route('/my/page', type='http', auth='public', website=True)
    def my_page(self, **kw):
        # Content rendered in website's current language
        return request.render('my_module.my_page_template', {
            'title': _("My Page Title"),
        })
```

---

## Testing Translations

### Test Translated Values
```python
def test_translation(self):
    """Test field translation works."""
    # Create record with English name
    record = self.env['my.model'].create({
        'name': 'English Name',
    })

    # Set French translation
    record.with_context(lang='fr_FR').write({
        'name': 'Nom Français',
    })

    # Verify translations
    self.assertEqual(record.name, 'English Name')
    self.assertEqual(
        record.with_context(lang='fr_FR').name,
        'Nom Français'
    )
```

---

## Summary

| Element | Translatable | Method |
|---------|--------------|--------|
| Field labels | Yes | `string=` attribute |
| Field help | Yes | `help=` attribute |
| Selection labels | Yes | Tuple values |
| Field content | Optional | `translate=True` |
| Error messages | Yes | `_()` function |
| Button labels | Yes | `string=` in XML |
| Menu names | Yes | `name=` in XML |
| Report text | Yes | Static XML text |
| Log messages | No | Keep in English |
