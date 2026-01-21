# Attachment and Binary Field Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ATTACHMENT & BINARY FIELD PATTERNS                                          ║
║  File uploads, images, documents, and attachments                            ║
║  Use for handling files, images, and documents in Odoo                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Binary Field Types

| Field Type | Use Case |
|------------|----------|
| `Binary` | Generic file storage |
| `Image` | Image with auto-resize |

---

## Basic Binary Fields

### File Upload Field
```python
from odoo import fields, models


class MyModel(models.Model):
    _name = 'my.model'

    # Basic binary field
    document = fields.Binary(string='Document')
    document_name = fields.Char(string='Document Name')

    # Binary with specific attachment flag
    attachment = fields.Binary(
        string='Attachment',
        attachment=True,  # Store as ir.attachment
    )
    attachment_name = fields.Char(string='Attachment Name')
```

### Image Field
```python
class MyModel(models.Model):
    _name = 'my.model'

    # Image field (auto-resizes)
    image = fields.Image(string='Image')

    # Image with max dimensions
    image_1920 = fields.Image(
        string='Image',
        max_width=1920,
        max_height=1920,
    )

    # Multiple image sizes (common pattern)
    image_1920 = fields.Image(max_width=1920, max_height=1920)
    image_1024 = fields.Image(
        related='image_1920',
        max_width=1024,
        max_height=1024,
        store=True,
    )
    image_512 = fields.Image(
        related='image_1920',
        max_width=512,
        max_height=512,
        store=True,
    )
    image_256 = fields.Image(
        related='image_1920',
        max_width=256,
        max_height=256,
        store=True,
    )
    image_128 = fields.Image(
        related='image_1920',
        max_width=128,
        max_height=128,
        store=True,
    )
```

---

## Views for Binary Fields

### Form View - File Upload
```xml
<form>
    <sheet>
        <group>
            <!-- File upload with filename -->
            <field name="document" filename="document_name"/>
            <field name="document_name" invisible="1"/>
        </group>
    </sheet>
</form>
```

### Form View - Image
```xml
<form>
    <sheet>
        <!-- Image at top of form (like res.partner) -->
        <field name="image_1920" widget="image" class="oe_avatar"
               options="{'preview_image': 'image_128'}"/>

        <!-- Or in a group -->
        <group>
            <field name="image" widget="image"/>
        </group>
    </sheet>
</form>
```

### Tree View - Image
```xml
<tree>
    <field name="image_128" widget="image" options="{'size': [32, 32]}"/>
    <field name="name"/>
</tree>
```

### Kanban View - Image
```xml
<kanban>
    <field name="image_128"/>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <div class="o_kanban_image">
                    <img t-att-src="kanban_image('my.model', 'image_128', record.id.raw_value)"
                         alt="Image" class="o_image_64_cover"/>
                </div>
                <div class="oe_kanban_details">
                    <field name="name"/>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

---

## ir.attachment Model

### Working with Attachments
```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread']  # For attachment tracking

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments',
    )

    # Or One2many for owned attachments
    document_ids = fields.One2many(
        'ir.attachment',
        'res_id',
        domain=[('res_model', '=', 'my.model')],
        string='Documents',
    )
```

### Creating Attachments
```python
def action_create_attachment(self):
    """Create attachment from binary data."""
    import base64

    attachment = self.env['ir.attachment'].create({
        'name': 'my_file.pdf',
        'type': 'binary',
        'datas': base64.b64encode(b'file content'),
        'res_model': self._name,
        'res_id': self.id,
        'mimetype': 'application/pdf',
    })
    return attachment

def action_attach_file(self, file_content, filename):
    """Attach file to record."""
    return self.env['ir.attachment'].create({
        'name': filename,
        'type': 'binary',
        'datas': base64.b64encode(file_content),
        'res_model': self._name,
        'res_id': self.id,
    })
```

### Reading Attachment Content
```python
def get_attachment_content(self, attachment_id):
    """Get attachment file content."""
    import base64

    attachment = self.env['ir.attachment'].browse(attachment_id)
    if attachment.exists():
        return base64.b64decode(attachment.datas)
    return None
```

### Deleting Attachments
```python
def action_cleanup_attachments(self):
    """Remove orphan attachments."""
    attachments = self.env['ir.attachment'].search([
        ('res_model', '=', self._name),
        ('res_id', '=', 0),  # Orphan attachments
    ])
    attachments.unlink()
```

---

## File Upload Controller

### Basic Upload Endpoint
```python
from odoo import http
from odoo.http import request
import base64


class FileUploadController(http.Controller):

    @http.route('/my_module/upload', type='http', auth='user',
                methods=['POST'], csrf=False)
    def upload_file(self, file, record_id, **kwargs):
        """Handle file upload."""
        if not file:
            return request.make_json_response({'error': 'No file'}, status=400)

        # Read file content
        file_content = file.read()
        file_name = file.filename

        # Create attachment
        attachment = request.env['ir.attachment'].sudo().create({
            'name': file_name,
            'type': 'binary',
            'datas': base64.b64encode(file_content),
            'res_model': 'my.model',
            'res_id': int(record_id),
        })

        return request.make_json_response({
            'success': True,
            'attachment_id': attachment.id,
        })
```

### Download Endpoint
```python
@http.route('/my_module/download/<int:attachment_id>', type='http',
            auth='user')
def download_file(self, attachment_id, **kwargs):
    """Download attachment."""
    attachment = request.env['ir.attachment'].sudo().browse(attachment_id)

    if not attachment.exists():
        return request.not_found()

    # Check access
    attachment.check('read')

    return request.make_response(
        base64.b64decode(attachment.datas),
        headers=[
            ('Content-Type', attachment.mimetype or 'application/octet-stream'),
            ('Content-Disposition', f'attachment; filename="{attachment.name}"'),
        ]
    )
```

---

## Image Processing

### Resize Image
```python
import base64
from io import BytesIO
from PIL import Image


def resize_image(self, image_data, max_width=1024, max_height=1024):
    """Resize image to max dimensions."""
    if not image_data:
        return image_data

    # Decode base64
    image_bytes = base64.b64decode(image_data)
    img = Image.open(BytesIO(image_bytes))

    # Calculate new size maintaining aspect ratio
    img.thumbnail((max_width, max_height), Image.LANCZOS)

    # Convert back to base64
    buffer = BytesIO()
    img_format = img.format or 'PNG'
    img.save(buffer, format=img_format)

    return base64.b64encode(buffer.getvalue())
```

### Generate Thumbnail
```python
def generate_thumbnail(self, image_data, size=(128, 128)):
    """Generate thumbnail from image."""
    if not image_data:
        return False

    image_bytes = base64.b64decode(image_data)
    img = Image.open(BytesIO(image_bytes))

    # Create thumbnail
    img.thumbnail(size, Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format='PNG')

    return base64.b64encode(buffer.getvalue())
```

### Image from URL
```python
import requests
import base64


def image_from_url(self, url):
    """Fetch image from URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return base64.b64encode(response.content)
    except Exception:
        return False
```

---

## Document Preview Widget

### PDF Preview
```xml
<form>
    <sheet>
        <group>
            <!-- PDF viewer widget -->
            <field name="pdf_document" widget="pdf_viewer"/>
        </group>
    </sheet>
</form>
```

### Image Preview with Zoom
```xml
<field name="image" widget="image" options="{'zoom': true, 'zoom_delay': 500}"/>
```

---

## Signature Field

### Model Definition
```python
class MyModel(models.Model):
    _name = 'my.model'

    signature = fields.Binary(string='Signature')
```

### View
```xml
<form>
    <sheet>
        <group>
            <field name="signature" widget="signature"/>
        </group>
    </sheet>
</form>
```

---

## Many Attachments Pattern

### Attachment Button in Form
```xml
<form>
    <sheet>
        <div class="oe_button_box" name="button_box">
            <button name="action_view_attachments" type="object"
                    class="oe_stat_button" icon="fa-files-o">
                <div class="o_field_widget o_stat_info">
                    <span class="o_stat_value">
                        <field name="attachment_count" widget="statinfo"/>
                    </span>
                    <span class="o_stat_text">Attachments</span>
                </div>
            </button>
        </div>
    </sheet>
</form>
```

### Attachment Count and Action
```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread']

    attachment_count = fields.Integer(
        compute='_compute_attachment_count',
        string='Attachments',
    )

    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', self._name),
                ('res_id', '=', record.id),
            ])

    def action_view_attachments(self):
        """Open attachments view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attachments',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [
                ('res_model', '=', self._name),
                ('res_id', '=', self.id),
            ],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            },
        }
```

---

## File Type Validation

### Validate File Extension
```python
from odoo.exceptions import ValidationError
import base64
import mimetypes


@api.constrains('document', 'document_name')
def _check_document(self):
    """Validate document type."""
    allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
    allowed_mimetypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ]

    for record in self:
        if record.document and record.document_name:
            # Check extension
            ext = '.' + record.document_name.rsplit('.', 1)[-1].lower()
            if ext not in allowed_extensions:
                raise ValidationError(
                    f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
                )

            # Check mimetype
            mimetype = mimetypes.guess_type(record.document_name)[0]
            if mimetype and mimetype not in allowed_mimetypes:
                raise ValidationError(f"Invalid file type: {mimetype}")
```

### Validate Image
```python
@api.constrains('image')
def _check_image(self):
    """Validate image format and size."""
    max_size = 10 * 1024 * 1024  # 10 MB
    allowed_formats = ['PNG', 'JPEG', 'JPG', 'GIF', 'WEBP']

    for record in self:
        if record.image:
            # Check size
            image_data = base64.b64decode(record.image)
            if len(image_data) > max_size:
                raise ValidationError(
                    f"Image too large. Maximum size: {max_size // 1024 // 1024} MB"
                )

            # Check format
            try:
                img = Image.open(BytesIO(image_data))
                if img.format.upper() not in allowed_formats:
                    raise ValidationError(
                        f"Invalid image format. Allowed: {', '.join(allowed_formats)}"
                    )
            except Exception as e:
                raise ValidationError(f"Invalid image: {str(e)}")
```

---

## Export/Import Binary Data

### Export Attachment to File
```python
import os


def export_attachments(self, path):
    """Export all attachments to filesystem."""
    attachments = self.env['ir.attachment'].search([
        ('res_model', '=', self._name),
        ('res_id', '=', self.id),
    ])

    for attachment in attachments:
        file_path = os.path.join(path, attachment.name)
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(attachment.datas))

    return len(attachments)
```

### Import Files as Attachments
```python
def import_files(self, file_paths):
    """Import files as attachments."""
    attachments = []

    for file_path in file_paths:
        with open(file_path, 'rb') as f:
            content = f.read()

        attachment = self.env['ir.attachment'].create({
            'name': os.path.basename(file_path),
            'type': 'binary',
            'datas': base64.b64encode(content),
            'res_model': self._name,
            'res_id': self.id,
        })
        attachments.append(attachment.id)

    return attachments
```

---

## Best Practices

1. **Use Image field for images** - Auto-resize and optimization
2. **Store as attachment** - `attachment=True` for large files
3. **Keep filename field** - Pair Binary with Char for filename
4. **Validate file types** - Security against malicious uploads
5. **Set size limits** - Prevent memory issues
6. **Generate thumbnails** - Multiple sizes for performance
7. **Use ir.attachment** - For multiple files per record
8. **Clean up orphans** - Remove unused attachments
9. **Check access rights** - Verify permissions on download
10. **Handle encoding** - Always use base64 for binary transport
