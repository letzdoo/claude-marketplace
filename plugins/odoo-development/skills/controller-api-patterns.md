# Controller and API Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  CONTROLLER & API PATTERNS                                                   ║
║  HTTP controllers, REST endpoints, and web routes                            ║
║  Use for APIs, webhooks, and custom web endpoints                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## File Structure

```
my_module/
├── controllers/
│   ├── __init__.py
│   └── main.py
└── __manifest__.py
```

### __init__.py
```python
from . import main
```

---

## Basic Controller

```python
from odoo import http
from odoo.http import request


class MyController(http.Controller):

    @http.route('/my_module/hello', type='http', auth='public')
    def hello(self):
        """Simple public endpoint."""
        return "Hello, World!"

    @http.route('/my_module/data', type='json', auth='user')
    def get_data(self):
        """JSON endpoint requiring authentication."""
        records = request.env['my.model'].search([])
        return {
            'status': 'success',
            'count': len(records),
            'data': records.read(['name', 'state']),
        }
```

---

## Route Decorators

### Basic Parameters
```python
@http.route(
    route='/my_module/endpoint',
    type='http',           # 'http' or 'json'
    auth='user',           # 'public', 'user', 'none'
    methods=['GET', 'POST'],
    website=False,         # True for website controllers
    csrf=True,             # CSRF protection (default True)
)
```

### Auth Types
| Auth | Description |
|------|-------------|
| `public` | No login required, uses public user |
| `user` | Login required |
| `none` | No user context, manual handling |

### Route Parameters
```python
# URL parameters
@http.route('/my_module/record/<int:record_id>')
def get_record(self, record_id):
    record = request.env['my.model'].browse(record_id)
    return record.name

# Multiple parameters
@http.route('/my_module/<model>/<int:id>/action')
def model_action(self, model, id):
    record = request.env[model].browse(id)
    return str(record)

# Optional parameters
@http.route('/my_module/search')
def search(self, query='', limit=10, **kw):
    records = request.env['my.model'].search(
        [('name', 'ilike', query)],
        limit=int(limit)
    )
    return str(records.ids)
```

---

## HTTP Controllers

### GET Endpoint
```python
@http.route('/api/v1/records', type='http', auth='user', methods=['GET'])
def list_records(self, **kw):
    """List records with pagination."""
    limit = int(kw.get('limit', 20))
    offset = int(kw.get('offset', 0))

    records = request.env['my.model'].search(
        [], limit=limit, offset=offset
    )

    data = []
    for record in records:
        data.append({
            'id': record.id,
            'name': record.name,
            'state': record.state,
        })

    return request.make_response(
        json.dumps({'data': data}),
        headers=[('Content-Type', 'application/json')]
    )
```

### POST Endpoint
```python
@http.route('/api/v1/records', type='http', auth='user',
            methods=['POST'], csrf=False)
def create_record(self, **post):
    """Create new record."""
    try:
        record = request.env['my.model'].create({
            'name': post.get('name'),
            'description': post.get('description'),
        })

        return request.make_response(
            json.dumps({
                'status': 'success',
                'id': record.id,
            }),
            headers=[('Content-Type', 'application/json')]
        )
    except Exception as e:
        return request.make_response(
            json.dumps({
                'status': 'error',
                'message': str(e),
            }),
            status=400,
            headers=[('Content-Type', 'application/json')]
        )
```

---

## JSON-RPC Controllers

### Basic JSON Endpoint
```python
@http.route('/api/v1/json/records', type='json', auth='user')
def json_list_records(self, domain=None, fields=None, limit=100):
    """JSON-RPC endpoint for listing records."""
    domain = domain or []
    fields = fields or ['name', 'state']

    records = request.env['my.model'].search_read(
        domain, fields, limit=limit
    )

    return {
        'status': 'success',
        'count': len(records),
        'records': records,
    }
```

### JSON with Validation
```python
@http.route('/api/v1/json/create', type='json', auth='user')
def json_create(self, name, **kwargs):
    """Create record with validation."""
    if not name:
        return {
            'status': 'error',
            'message': 'Name is required',
        }

    try:
        vals = {'name': name}
        if kwargs.get('partner_id'):
            vals['partner_id'] = int(kwargs['partner_id'])

        record = request.env['my.model'].create(vals)

        return {
            'status': 'success',
            'id': record.id,
            'name': record.name,
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
        }
```

---

## REST API Pattern

### Complete CRUD Controller
```python
import json
from odoo import http
from odoo.http import request, Response


class MyAPIController(http.Controller):
    """REST API for my.model"""

    def _get_record(self, record_id):
        """Helper to get record with error handling."""
        record = request.env['my.model'].browse(record_id)
        if not record.exists():
            return None
        return record

    def _json_response(self, data, status=200):
        """Helper to create JSON response."""
        return Response(
            json.dumps(data),
            status=status,
            mimetype='application/json'
        )

    # LIST
    @http.route('/api/v1/mymodel', type='http', auth='user',
                methods=['GET'], csrf=False)
    def list(self, **kw):
        """GET /api/v1/mymodel - List all records."""
        domain = []
        if kw.get('state'):
            domain.append(('state', '=', kw['state']))

        records = request.env['my.model'].search_read(
            domain,
            ['id', 'name', 'state', 'create_date'],
            limit=int(kw.get('limit', 100)),
            offset=int(kw.get('offset', 0)),
        )

        return self._json_response({
            'status': 'success',
            'data': records,
        })

    # GET
    @http.route('/api/v1/mymodel/<int:id>', type='http', auth='user',
                methods=['GET'], csrf=False)
    def get(self, id):
        """GET /api/v1/mymodel/{id} - Get single record."""
        record = self._get_record(id)
        if not record:
            return self._json_response(
                {'status': 'error', 'message': 'Not found'},
                status=404
            )

        return self._json_response({
            'status': 'success',
            'data': {
                'id': record.id,
                'name': record.name,
                'state': record.state,
                'partner_id': record.partner_id.id,
                'partner_name': record.partner_id.name,
            },
        })

    # CREATE
    @http.route('/api/v1/mymodel', type='http', auth='user',
                methods=['POST'], csrf=False)
    def create(self, **post):
        """POST /api/v1/mymodel - Create record."""
        try:
            required = ['name']
            for field in required:
                if not post.get(field):
                    return self._json_response(
                        {'status': 'error', 'message': f'{field} is required'},
                        status=400
                    )

            vals = {
                'name': post['name'],
            }
            if post.get('partner_id'):
                vals['partner_id'] = int(post['partner_id'])

            record = request.env['my.model'].create(vals)

            return self._json_response({
                'status': 'success',
                'id': record.id,
            }, status=201)

        except Exception as e:
            return self._json_response(
                {'status': 'error', 'message': str(e)},
                status=500
            )

    # UPDATE
    @http.route('/api/v1/mymodel/<int:id>', type='http', auth='user',
                methods=['PUT', 'PATCH'], csrf=False)
    def update(self, id, **post):
        """PUT/PATCH /api/v1/mymodel/{id} - Update record."""
        record = self._get_record(id)
        if not record:
            return self._json_response(
                {'status': 'error', 'message': 'Not found'},
                status=404
            )

        try:
            vals = {}
            if 'name' in post:
                vals['name'] = post['name']
            if 'state' in post:
                vals['state'] = post['state']

            if vals:
                record.write(vals)

            return self._json_response({
                'status': 'success',
                'id': record.id,
            })

        except Exception as e:
            return self._json_response(
                {'status': 'error', 'message': str(e)},
                status=500
            )

    # DELETE
    @http.route('/api/v1/mymodel/<int:id>', type='http', auth='user',
                methods=['DELETE'], csrf=False)
    def delete(self, id):
        """DELETE /api/v1/mymodel/{id} - Delete record."""
        record = self._get_record(id)
        if not record:
            return self._json_response(
                {'status': 'error', 'message': 'Not found'},
                status=404
            )

        try:
            record.unlink()
            return self._json_response({
                'status': 'success',
                'message': 'Deleted',
            })

        except Exception as e:
            return self._json_response(
                {'status': 'error', 'message': str(e)},
                status=500
            )
```

---

## Webhook Endpoint

```python
import hmac
import hashlib

class WebhookController(http.Controller):

    @http.route('/webhook/my_module', type='json', auth='none',
                methods=['POST'], csrf=False)
    def webhook_handler(self):
        """Handle incoming webhook."""
        # Get raw data
        data = request.jsonrequest

        # Verify signature (example)
        signature = request.httprequest.headers.get('X-Signature')
        secret = request.env['ir.config_parameter'].sudo().get_param(
            'my_module.webhook_secret'
        )

        if not self._verify_signature(data, signature, secret):
            return {'status': 'error', 'message': 'Invalid signature'}

        # Process webhook
        try:
            event_type = data.get('event')
            payload = data.get('payload', {})

            if event_type == 'order.created':
                self._handle_order_created(payload)
            elif event_type == 'payment.received':
                self._handle_payment_received(payload)

            return {'status': 'success'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _verify_signature(self, data, signature, secret):
        """Verify webhook signature."""
        if not signature or not secret:
            return False
        expected = hmac.new(
            secret.encode(),
            json.dumps(data).encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)

    def _handle_order_created(self, payload):
        """Handle order created event."""
        request.env['my.model'].sudo().create({
            'name': payload.get('order_id'),
            'external_id': payload.get('id'),
        })
```

---

## File Download/Upload

### File Download
```python
@http.route('/my_module/download/<int:id>', type='http', auth='user')
def download_file(self, id):
    """Download file attachment."""
    record = request.env['my.model'].browse(id)
    if not record.exists() or not record.file:
        return request.not_found()

    return request.make_response(
        base64.b64decode(record.file),
        headers=[
            ('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', f'attachment; filename="{record.filename}"'),
        ]
    )
```

### File Upload
```python
@http.route('/my_module/upload', type='http', auth='user',
            methods=['POST'], csrf=False)
def upload_file(self, **post):
    """Upload file."""
    file = post.get('file')
    if not file:
        return json.dumps({'error': 'No file provided'})

    try:
        content = base64.b64encode(file.read())
        filename = file.filename

        record = request.env['my.model'].create({
            'name': filename,
            'file': content,
            'filename': filename,
        })

        return json.dumps({
            'status': 'success',
            'id': record.id,
        })

    except Exception as e:
        return json.dumps({'error': str(e)})
```

---

## Authentication

### API Key Authentication
```python
class APIKeyController(http.Controller):

    def _check_api_key(self):
        """Validate API key from header."""
        api_key = request.httprequest.headers.get('X-API-Key')
        if not api_key:
            return False

        valid_key = request.env['ir.config_parameter'].sudo().get_param(
            'my_module.api_key'
        )
        return api_key == valid_key

    @http.route('/api/secure/data', type='json', auth='none', csrf=False)
    def secure_endpoint(self):
        """Endpoint with API key auth."""
        if not self._check_api_key():
            return {'error': 'Invalid API key'}, 401

        # Process request with sudo (no user context)
        data = request.env['my.model'].sudo().search_read([], ['name'])
        return {'data': data}
```

---

## Best Practices

1. **Use appropriate auth** - `public` for public APIs, `user` for authenticated
2. **Handle errors gracefully** - Return proper HTTP status codes
3. **Validate input** - Check required fields and types
4. **Use sudo carefully** - Only when necessary for public endpoints
5. **CSRF protection** - Disable only for legitimate API endpoints
6. **Rate limiting** - Implement for public APIs
7. **Logging** - Log API requests for debugging
8. **Documentation** - Document endpoints for consumers
