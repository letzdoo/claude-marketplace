# External API Integration Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  EXTERNAL API INTEGRATION PATTERNS                                           ║
║  Connecting to third-party services, REST/SOAP APIs, and webhooks            ║
║  Use for payment gateways, shipping providers, CRM sync, etc.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Configuration Model

### API Credentials Storage
```python
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import requests


class ExternalAPIConfig(models.Model):
    _name = 'external.api.config'
    _description = 'External API Configuration'

    name = fields.Char(string='Name', required=True)
    api_url = fields.Char(string='API URL', required=True)
    api_key = fields.Char(string='API Key', groups='base.group_system')
    api_secret = fields.Char(string='API Secret', groups='base.group_system')
    environment = fields.Selection(
        selection=[
            ('sandbox', 'Sandbox'),
            ('production', 'Production'),
        ],
        string='Environment',
        default='sandbox',
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
    last_sync = fields.Datetime(string='Last Sync', readonly=True)

    @api.constrains('api_url')
    def _check_api_url(self):
        for config in self:
            if not config.api_url.startswith(('http://', 'https://')):
                raise ValidationError("API URL must start with http:// or https://")

    def action_test_connection(self):
        """Test API connection."""
        self.ensure_one()
        try:
            response = self._make_request('GET', '/health')
            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': 'Connection successful!',
                        'type': 'success',
                    }
                }
        except Exception as e:
            raise ValidationError(f"Connection failed: {str(e)}")
```

### System Parameters (Alternative)
```python
# Store in ir.config_parameter
def _get_api_key(self):
    """Get API key from system parameters."""
    return self.env['ir.config_parameter'].sudo().get_param(
        'my_module.api_key', default=''
    )

def _set_api_key(self, value):
    """Set API key in system parameters."""
    self.env['ir.config_parameter'].sudo().set_param(
        'my_module.api_key', value
    )
```

---

## HTTP Client Mixin

### Reusable API Client
```python
import json
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_logger = logging.getLogger(__name__)


class APIClientMixin(models.AbstractModel):
    _name = 'api.client.mixin'
    _description = 'API Client Mixin'

    def _get_session(self):
        """Get requests session with retry logic."""
        session = requests.Session()

        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def _get_headers(self):
        """Get default headers."""
        config = self._get_api_config()
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {config.api_key}',
            'X-API-Version': '2024-01',
        }

    def _get_api_config(self):
        """Get API configuration for current company."""
        config = self.env['external.api.config'].search([
            ('company_id', '=', self.env.company.id),
            ('active', '=', True),
        ], limit=1)

        if not config:
            raise ValidationError("No API configuration found for this company.")

        return config

    def _make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request to external API."""
        config = self._get_api_config()
        url = f"{config.api_url.rstrip('/')}/{endpoint.lstrip('/')}"

        session = self._get_session()
        headers = self._get_headers()

        _logger.info("API Request: %s %s", method, url)

        try:
            response = session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=30,
            )

            _logger.info("API Response: %s", response.status_code)

            if response.status_code >= 400:
                self._handle_error(response)

            return response

        except requests.Timeout:
            _logger.error("API Timeout: %s", url)
            raise ValidationError("API request timed out. Please try again.")

        except requests.RequestException as e:
            _logger.error("API Error: %s", str(e))
            raise ValidationError(f"API request failed: {str(e)}")

    def _handle_error(self, response):
        """Handle API error response."""
        try:
            error_data = response.json()
            message = error_data.get('message', response.text)
        except json.JSONDecodeError:
            message = response.text

        _logger.error("API Error %s: %s", response.status_code, message)

        if response.status_code == 401:
            raise ValidationError("Authentication failed. Check your API credentials.")
        elif response.status_code == 403:
            raise ValidationError("Access forbidden. Check your API permissions.")
        elif response.status_code == 404:
            raise ValidationError("Resource not found.")
        elif response.status_code == 429:
            raise ValidationError("Rate limit exceeded. Please try again later.")
        else:
            raise ValidationError(f"API Error ({response.status_code}): {message}")
```

---

## Sync Patterns

### Pull Sync (Import from External)
```python
class ExternalProduct(models.Model):
    _name = 'external.product'
    _description = 'External Product Sync'
    _inherit = ['api.client.mixin']

    external_id = fields.Char(string='External ID', index=True)
    product_id = fields.Many2one('product.product', string='Odoo Product')
    sync_date = fields.Datetime(string='Last Sync')
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('error', 'Error'),
    ], default='pending')
    sync_error = fields.Text(string='Sync Error')

    @api.model
    def _cron_sync_products(self):
        """Cron job to sync products from external API."""
        _logger.info("Starting product sync from external API")

        try:
            response = self._make_request('GET', '/products', params={
                'updated_since': self._get_last_sync_date(),
                'limit': 100,
            })
            products = response.json().get('data', [])

            for product_data in products:
                self._sync_single_product(product_data)

            _logger.info("Synced %d products", len(products))

        except Exception as e:
            _logger.error("Product sync failed: %s", str(e))

    def _sync_single_product(self, data):
        """Sync single product from external data."""
        external_id = str(data['id'])

        # Find or create mapping
        mapping = self.search([('external_id', '=', external_id)], limit=1)
        if not mapping:
            mapping = self.create({'external_id': external_id})

        try:
            # Find or create Odoo product
            product = mapping.product_id
            if not product:
                product = self.env['product.product'].create({
                    'name': data['name'],
                    'default_code': data.get('sku'),
                    'list_price': data.get('price', 0),
                })
                mapping.product_id = product
            else:
                product.write({
                    'name': data['name'],
                    'list_price': data.get('price', 0),
                })

            mapping.write({
                'sync_date': fields.Datetime.now(),
                'sync_status': 'synced',
                'sync_error': False,
            })

        except Exception as e:
            mapping.write({
                'sync_status': 'error',
                'sync_error': str(e),
            })
            _logger.error("Failed to sync product %s: %s", external_id, str(e))
```

### Push Sync (Export to External)
```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    external_customer_id = fields.Char(string='External Customer ID')
    sync_to_external = fields.Boolean(string='Sync to External', default=True)

    def write(self, vals):
        """Override write to trigger external sync."""
        result = super().write(vals)

        # Sync if relevant fields changed
        sync_fields = {'name', 'email', 'phone', 'street', 'city'}
        if self.sync_to_external and sync_fields & set(vals.keys()):
            self._sync_to_external_api()

        return result

    def _sync_to_external_api(self):
        """Push customer data to external API."""
        for partner in self:
            if not partner.sync_to_external:
                continue

            data = {
                'name': partner.name,
                'email': partner.email,
                'phone': partner.phone,
                'address': {
                    'street': partner.street,
                    'city': partner.city,
                    'zip': partner.zip,
                    'country': partner.country_id.code,
                },
            }

            try:
                api_client = self.env['api.client.mixin']

                if partner.external_customer_id:
                    # Update existing
                    response = api_client._make_request(
                        'PUT',
                        f'/customers/{partner.external_customer_id}',
                        data=data
                    )
                else:
                    # Create new
                    response = api_client._make_request(
                        'POST', '/customers', data=data
                    )
                    result = response.json()
                    partner.external_customer_id = result['id']

            except Exception as e:
                _logger.error("Failed to sync partner %s: %s", partner.id, str(e))
```

### Bidirectional Sync
```python
class SyncManager(models.Model):
    _name = 'sync.manager'
    _description = 'Bidirectional Sync Manager'
    _inherit = ['api.client.mixin']

    @api.model
    def _cron_full_sync(self):
        """Full bidirectional sync."""
        self._pull_changes()
        self._push_changes()

    def _pull_changes(self):
        """Pull changes from external system."""
        last_sync = self._get_last_sync_timestamp('pull')

        response = self._make_request('GET', '/changes', params={
            'since': last_sync,
            'types': 'customer,product,order',
        })

        for change in response.json().get('changes', []):
            self._process_incoming_change(change)

        self._set_last_sync_timestamp('pull')

    def _push_changes(self):
        """Push local changes to external system."""
        # Get records modified since last push
        last_sync = self._get_last_sync_timestamp('push')

        modified_partners = self.env['res.partner'].search([
            ('write_date', '>', last_sync),
            ('sync_to_external', '=', True),
        ])

        for partner in modified_partners:
            partner._sync_to_external_api()

        self._set_last_sync_timestamp('push')
```

---

## Webhook Handling

### Incoming Webhooks
```python
from odoo import http
from odoo.http import request
import hmac
import hashlib


class WebhookController(http.Controller):

    @http.route('/webhook/external', type='json', auth='none',
                methods=['POST'], csrf=False)
    def handle_webhook(self):
        """Handle incoming webhook from external service."""
        # Verify signature
        signature = request.httprequest.headers.get('X-Signature')
        if not self._verify_signature(signature):
            return {'error': 'Invalid signature'}, 401

        data = request.jsonrequest
        event_type = data.get('event')

        _logger.info("Received webhook: %s", event_type)

        try:
            if event_type == 'customer.created':
                self._handle_customer_created(data['payload'])
            elif event_type == 'customer.updated':
                self._handle_customer_updated(data['payload'])
            elif event_type == 'order.completed':
                self._handle_order_completed(data['payload'])
            else:
                _logger.warning("Unknown webhook event: %s", event_type)

            return {'status': 'success'}

        except Exception as e:
            _logger.error("Webhook processing failed: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    def _verify_signature(self, signature):
        """Verify webhook signature."""
        if not signature:
            return False

        secret = request.env['ir.config_parameter'].sudo().get_param(
            'my_module.webhook_secret'
        )
        if not secret:
            return False

        raw_body = request.httprequest.get_data()
        expected = hmac.new(
            secret.encode(),
            raw_body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected)

    def _handle_customer_created(self, payload):
        """Process customer creation webhook."""
        partner = request.env['res.partner'].sudo().create({
            'name': payload['name'],
            'email': payload['email'],
            'external_customer_id': payload['id'],
        })
        _logger.info("Created partner %s from webhook", partner.id)
```

### Outgoing Webhooks
```python
class WebhookSender(models.Model):
    _name = 'webhook.sender'
    _description = 'Outgoing Webhook Sender'

    @api.model
    def send_webhook(self, event_type, payload, url=None):
        """Send webhook to external endpoint."""
        if not url:
            url = self.env['ir.config_parameter'].sudo().get_param(
                'my_module.webhook_url'
            )

        if not url:
            _logger.warning("No webhook URL configured")
            return False

        data = {
            'event': event_type,
            'timestamp': fields.Datetime.now().isoformat(),
            'payload': payload,
        }

        # Sign the payload
        secret = self.env['ir.config_parameter'].sudo().get_param(
            'my_module.webhook_secret'
        )
        signature = hmac.new(
            secret.encode(),
            json.dumps(data).encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            'Content-Type': 'application/json',
            'X-Signature': signature,
        }

        try:
            response = requests.post(
                url, json=data, headers=headers, timeout=10
            )
            response.raise_for_status()
            _logger.info("Webhook sent successfully: %s", event_type)
            return True

        except Exception as e:
            _logger.error("Webhook failed: %s", str(e))
            # Queue for retry
            self._queue_webhook_retry(event_type, payload, url)
            return False
```

---

## OAuth2 Integration

### OAuth2 Token Management
```python
from datetime import timedelta


class OAuth2Config(models.Model):
    _name = 'oauth2.config'
    _description = 'OAuth2 Configuration'

    name = fields.Char(string='Name', required=True)
    client_id = fields.Char(string='Client ID', required=True)
    client_secret = fields.Char(
        string='Client Secret',
        required=True,
        groups='base.group_system',
    )
    auth_url = fields.Char(string='Authorization URL')
    token_url = fields.Char(string='Token URL', required=True)
    scope = fields.Char(string='Scope')

    access_token = fields.Char(string='Access Token', groups='base.group_system')
    refresh_token = fields.Char(string='Refresh Token', groups='base.group_system')
    token_expiry = fields.Datetime(string='Token Expiry')

    def get_access_token(self):
        """Get valid access token, refreshing if needed."""
        self.ensure_one()

        if self.access_token and self.token_expiry:
            if fields.Datetime.now() < self.token_expiry - timedelta(minutes=5):
                return self.access_token

        # Token expired or missing, refresh
        if self.refresh_token:
            self._refresh_token()
        else:
            self._get_new_token()

        return self.access_token

    def _refresh_token(self):
        """Refresh the access token."""
        response = requests.post(self.token_url, data={
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        })

        if response.status_code != 200:
            raise ValidationError("Token refresh failed")

        self._process_token_response(response.json())

    def _get_new_token(self):
        """Get new token using client credentials."""
        response = requests.post(self.token_url, data={
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': self.scope,
        })

        if response.status_code != 200:
            raise ValidationError("Token acquisition failed")

        self._process_token_response(response.json())

    def _process_token_response(self, data):
        """Process token response and store tokens."""
        expires_in = data.get('expires_in', 3600)
        self.write({
            'access_token': data['access_token'],
            'refresh_token': data.get('refresh_token', self.refresh_token),
            'token_expiry': fields.Datetime.now() + timedelta(seconds=expires_in),
        })
```

---

## Rate Limiting

### Rate Limiter
```python
import time
from collections import deque


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period  # seconds
        self.calls = deque()

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()

        # Remove old calls outside the window
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()

        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                _logger.info("Rate limit reached, sleeping %.2fs", sleep_time)
                time.sleep(sleep_time)

        self.calls.append(time.time())


# Usage in API client
class APIClient(models.AbstractModel):
    _name = 'api.client'
    _rate_limiter = RateLimiter(max_calls=100, period=60)

    def _make_request(self, method, endpoint, **kwargs):
        self._rate_limiter.wait_if_needed()
        # ... rest of request logic
```

---

## Error Handling & Retry

### Retry with Exponential Backoff
```python
import time
from functools import wraps


def retry_on_failure(max_retries=3, backoff_factor=2):
    """Decorator for retry with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.Timeout, requests.ConnectionError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        sleep_time = backoff_factor ** attempt
                        _logger.warning(
                            "Attempt %d failed, retrying in %ds: %s",
                            attempt + 1, sleep_time, str(e)
                        )
                        time.sleep(sleep_time)
            raise last_exception
        return wrapper
    return decorator


class APIClientWithRetry(models.AbstractModel):
    _name = 'api.client.retry'

    @retry_on_failure(max_retries=3, backoff_factor=2)
    def _make_request(self, method, endpoint, **kwargs):
        # Request implementation
        pass
```

---

## Best Practices

1. **Never hardcode credentials** - Use ir.config_parameter or dedicated config model
2. **Use HTTPS** - Always use secure connections
3. **Implement retry logic** - Handle transient failures
4. **Log all API calls** - For debugging and audit
5. **Handle rate limits** - Implement backoff strategies
6. **Validate responses** - Don't trust external data
7. **Use timeouts** - Prevent hanging requests
8. **Queue heavy operations** - Don't block user actions
9. **Test with sandbox** - Use environment switching
10. **Secure webhooks** - Always verify signatures
