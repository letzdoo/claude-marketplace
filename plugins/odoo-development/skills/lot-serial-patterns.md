# Lot and Serial Number Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  LOT & SERIAL NUMBER PATTERNS                                                ║
║  Product traceability, batch tracking, and serial number management          ║
║  Use for inventory tracking, recalls, and compliance requirements            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Tracking Types

| Tracking | Description | Use Case |
|----------|-------------|----------|
| `none` | No tracking | Basic products |
| `lot` | Batch/Lot tracking | Multiple items per lot |
| `serial` | Serial number | One item per serial |

---

## Product Tracking Configuration

### Enable Tracking on Product
```python
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking'),
    ], string='Tracking', default='none', required=True)

# Create product with lot tracking
product = self.env['product.template'].create({
    'name': 'Pharmaceutical Product',
    'type': 'product',
    'tracking': 'lot',  # Batch tracking
})

# Create product with serial tracking
product_serial = self.env['product.template'].create({
    'name': 'Electronic Device',
    'type': 'product',
    'tracking': 'serial',  # Unique serial per unit
})
```

---

## Creating Lots and Serials

### Create Lot/Serial
```python
# Create a lot (batch)
lot = self.env['stock.lot'].create({
    'name': 'LOT-2024-001',
    'product_id': product.id,
    'company_id': self.env.company.id,
})

# With expiration date
lot_with_expiry = self.env['stock.lot'].create({
    'name': 'LOT-2024-002',
    'product_id': product.id,
    'company_id': self.env.company.id,
    'expiration_date': fields.Datetime.now() + timedelta(days=365),
    'use_date': fields.Datetime.now() + timedelta(days=300),
    'removal_date': fields.Datetime.now() + timedelta(days=350),
    'alert_date': fields.Datetime.now() + timedelta(days=280),
})
```

### Auto-Generate Serial Numbers
```python
def generate_serial_numbers(self, product, quantity, prefix='SN'):
    """Generate unique serial numbers."""
    serials = []
    for i in range(int(quantity)):
        serial = self.env['stock.lot'].create({
            'name': f"{prefix}-{fields.Date.today().strftime('%Y%m%d')}-{i+1:04d}",
            'product_id': product.id,
            'company_id': self.env.company.id,
        })
        serials.append(serial)
    return serials
```

---

## Stock Moves with Lots

### Create Move with Lot
```python
def create_move_with_lot(self, product, lot, qty, location_src, location_dest):
    """Create stock move with lot tracking."""
    move = self.env['stock.move'].create({
        'name': f'Move {product.name}',
        'product_id': product.id,
        'product_uom_qty': qty,
        'product_uom': product.uom_id.id,
        'location_id': location_src.id,
        'location_dest_id': location_dest.id,
    })

    # Create move line with lot
    self.env['stock.move.line'].create({
        'move_id': move.id,
        'product_id': product.id,
        'lot_id': lot.id,
        'quantity': qty,
        'product_uom_id': product.uom_id.id,
        'location_id': location_src.id,
        'location_dest_id': location_dest.id,
    })

    move._action_confirm()
    move._action_assign()
    move._action_done()

    return move
```

### Receive with New Lot
```python
def receive_with_lot(self, picking, product, qty, lot_name):
    """Receive products creating new lot."""
    # Find or create lot
    lot = self.env['stock.lot'].search([
        ('name', '=', lot_name),
        ('product_id', '=', product.id),
    ]) or self.env['stock.lot'].create({
        'name': lot_name,
        'product_id': product.id,
        'company_id': picking.company_id.id,
    })

    # Find the move for this product
    move = picking.move_ids.filtered(lambda m: m.product_id == product)

    # Set lot on move line
    move.move_line_ids.write({
        'lot_id': lot.id,
        'quantity': qty,
    })

    return lot
```

---

## Querying Lots

### Find Lots for Product
```python
def get_product_lots(self, product):
    """Get all lots for a product."""
    return self.env['stock.lot'].search([
        ('product_id', '=', product.id),
    ])

def get_available_lots(self, product, location=None):
    """Get lots with available stock."""
    domain = [('product_id', '=', product.id)]

    lots = self.env['stock.lot'].search(domain)

    available_lots = []
    for lot in lots:
        # Get quantity for this lot
        quants = self.env['stock.quant'].search([
            ('lot_id', '=', lot.id),
            ('location_id.usage', '=', 'internal'),
        ])
        if location:
            quants = quants.filtered(lambda q: q.location_id == location)

        qty = sum(quants.mapped('quantity'))
        if qty > 0:
            available_lots.append({
                'lot': lot,
                'quantity': qty,
                'expiration_date': lot.expiration_date,
            })

    return available_lots
```

### Get Stock by Lot
```python
def get_lot_stock(self, lot):
    """Get stock quantity for a specific lot."""
    quants = self.env['stock.quant'].search([
        ('lot_id', '=', lot.id),
        ('location_id.usage', '=', 'internal'),
    ])
    return sum(quants.mapped('quantity'))
```

---

## Expiration Date Tracking

### Product Expiration Fields
```python
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    use_expiration_date = fields.Boolean(
        string='Expiration Date',
        help='Track expiration dates on lots/serials',
    )

    # Default durations (in days)
    expiration_time = fields.Integer(string='Expiration Time')
    use_time = fields.Integer(string='Best Before Time')
    removal_time = fields.Integer(string='Removal Time')
    alert_time = fields.Integer(string='Alert Time')
```

### Auto-Calculate Expiration Dates
```python
class StockLot(models.Model):
    _inherit = 'stock.lot'

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-set expiration dates from product."""
        for vals in vals_list:
            if 'product_id' in vals:
                product = self.env['product.product'].browse(vals['product_id'])
                if product.use_expiration_date:
                    now = fields.Datetime.now()
                    if not vals.get('expiration_date') and product.expiration_time:
                        vals['expiration_date'] = now + timedelta(days=product.expiration_time)
                    if not vals.get('use_date') and product.use_time:
                        vals['use_date'] = now + timedelta(days=product.use_time)
                    if not vals.get('removal_date') and product.removal_time:
                        vals['removal_date'] = now + timedelta(days=product.removal_time)
                    if not vals.get('alert_date') and product.alert_time:
                        vals['alert_date'] = now + timedelta(days=product.alert_time)

        return super().create(vals_list)
```

### Check Expiring Lots
```python
def get_expiring_lots(self, days=30):
    """Find lots expiring within specified days."""
    deadline = fields.Datetime.now() + timedelta(days=days)
    return self.env['stock.lot'].search([
        ('expiration_date', '!=', False),
        ('expiration_date', '<=', deadline),
        ('expiration_date', '>', fields.Datetime.now()),
    ])

def get_expired_lots(self):
    """Find expired lots with stock."""
    expired_lots = self.env['stock.lot'].search([
        ('expiration_date', '<', fields.Datetime.now()),
    ])

    # Filter to only those with stock
    return expired_lots.filtered(
        lambda l: sum(l.quant_ids.filtered(
            lambda q: q.location_id.usage == 'internal'
        ).mapped('quantity')) > 0
    )
```

---

## FIFO/FEFO Removal Strategy

### Configure Removal Strategy
```python
# On location or category
location = self.env['stock.location'].browse(location_id)
location.write({
    'removal_strategy_id': self.env.ref('stock.removal_fifo').id,
})

# FEFO (First Expiry, First Out)
location.write({
    'removal_strategy_id': self.env.ref('stock.removal_fefo').id,
})
```

### Manual Lot Selection
```python
def select_lot_for_delivery(self, product, quantity, strategy='fifo'):
    """Select lots for delivery based on strategy."""
    lots = self.get_available_lots(product)

    if strategy == 'fefo':
        # Sort by expiration date (earliest first)
        lots = sorted(lots, key=lambda l: l['expiration_date'] or datetime.max)
    elif strategy == 'fifo':
        # Sort by lot creation date (oldest first)
        lots = sorted(lots, key=lambda l: l['lot'].create_date)

    selected = []
    remaining = quantity
    for lot_data in lots:
        if remaining <= 0:
            break
        take = min(lot_data['quantity'], remaining)
        selected.append({
            'lot_id': lot_data['lot'].id,
            'quantity': take,
        })
        remaining -= take

    return selected
```

---

## Serial Number Validation

### Unique Serial Check
```python
class StockLot(models.Model):
    _inherit = 'stock.lot'

    @api.constrains('name', 'product_id', 'company_id')
    def _check_unique_serial(self):
        """Ensure serial numbers are unique."""
        for lot in self:
            if lot.product_id.tracking == 'serial':
                duplicates = self.search([
                    ('id', '!=', lot.id),
                    ('name', '=', lot.name),
                    ('product_id', '=', lot.product_id.id),
                    ('company_id', '=', lot.company_id.id),
                ])
                if duplicates:
                    raise ValidationError(
                        f"Serial number {lot.name} already exists for this product."
                    )
```

### Serial Format Validation
```python
import re

@api.constrains('name')
def _check_serial_format(self):
    """Validate serial number format."""
    pattern = r'^[A-Z]{2}-\d{4}-\d{6}$'  # e.g., SN-2024-000001
    for lot in self:
        if lot.product_id.tracking == 'serial':
            if not re.match(pattern, lot.name):
                raise ValidationError(
                    f"Invalid serial format: {lot.name}. "
                    f"Expected format: XX-YYYY-NNNNNN"
                )
```

---

## Traceability Reports

### Get Lot History
```python
def get_lot_traceability(self, lot):
    """Get complete history of a lot."""
    moves = self.env['stock.move.line'].search([
        ('lot_id', '=', lot.id),
        ('state', '=', 'done'),
    ])

    history = []
    for move in moves.sorted('date'):
        history.append({
            'date': move.date,
            'reference': move.reference,
            'from_location': move.location_id.complete_name,
            'to_location': move.location_dest_id.complete_name,
            'quantity': move.quantity,
            'picking': move.picking_id.name if move.picking_id else None,
        })

    return history
```

### Upstream/Downstream Traceability
```python
def get_upstream_lots(self, lot):
    """Find source lots (for manufacturing)."""
    # Find production orders that consumed this lot
    consumed = self.env['stock.move.line'].search([
        ('lot_id', '=', lot.id),
        ('location_dest_id.usage', '=', 'production'),
    ])

    # Find resulting products
    productions = consumed.mapped('move_id.raw_material_production_id')
    return productions.mapped('lot_producing_id')

def get_downstream_lots(self, lot):
    """Find destination lots (for recalls)."""
    # Find where this lot was consumed in production
    consumed = self.env['stock.move.line'].search([
        ('lot_id', '=', lot.id),
        ('move_id.raw_material_production_id', '!=', False),
    ])

    return consumed.mapped('move_id.raw_material_production_id.lot_producing_id')
```

---

## Custom Fields on Lots

### Extend Lot Model
```python
class StockLot(models.Model):
    _inherit = 'stock.lot'

    supplier_lot = fields.Char(string='Supplier Lot Number')
    production_date = fields.Date(string='Production Date')
    certificate_ids = fields.Many2many(
        'ir.attachment',
        string='Quality Certificates',
    )
    notes = fields.Text(string='Notes')

    # Quality control
    qc_status = fields.Selection([
        ('pending', 'Pending QC'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('quarantine', 'Quarantine'),
    ], string='QC Status', default='pending')
```

---

## XML Data for Lots

### Pre-define Lots
```xml
<record id="lot_sample_001" model="stock.lot">
    <field name="name">SAMPLE-LOT-001</field>
    <field name="product_id" ref="product_sample"/>
    <field name="company_id" ref="base.main_company"/>
</record>
```

---

## Best Practices

1. **Choose tracking wisely** - Serial for unique items, lot for batches
2. **Use expiration dates** - For perishables and regulated products
3. **Validate formats** - Consistent naming conventions
4. **FEFO for perishables** - First expiry, first out
5. **Track QC status** - Before releasing to inventory
6. **Maintain traceability** - For recalls and compliance
7. **Supplier lot mapping** - Link to vendor's batch numbers
8. **Automate numbering** - Use sequences for consistency
9. **Regular audits** - Check expired/quarantined stock
10. **Document certificates** - Attach quality documents to lots
