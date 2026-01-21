# Stock and Inventory Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  STOCK & INVENTORY PATTERNS                                                  ║
║  Warehouse management, stock moves, and inventory operations                 ║
║  Use for inventory tracking, transfers, and logistics automation             ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Module Setup

### Manifest Dependencies
```python
{
    'name': 'My Stock Module',
    'version': '18.0.1.0.0',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_views.xml',
    ],
}
```

---

## Extending Stock Models

### Extend Product for Stock
```python
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_min_stock_qty = fields.Float(
        string='Minimum Stock Quantity',
        default=0.0,
        help='Alert when stock falls below this level',
    )
    x_max_stock_qty = fields.Float(
        string='Maximum Stock Quantity',
        default=0.0,
    )
    x_reorder_qty = fields.Float(
        string='Reorder Quantity',
        default=1.0,
    )
    x_stock_status = fields.Selection(
        selection=[
            ('ok', 'In Stock'),
            ('low', 'Low Stock'),
            ('out', 'Out of Stock'),
        ],
        string='Stock Status',
        compute='_compute_stock_status',
        store=True,
    )

    @api.depends('qty_available', 'x_min_stock_qty')
    def _compute_stock_status(self):
        for product in self:
            if product.qty_available <= 0:
                product.x_stock_status = 'out'
            elif product.qty_available < product.x_min_stock_qty:
                product.x_stock_status = 'low'
            else:
                product.x_stock_status = 'ok'
```

### Extend Stock Picking
```python
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_delivery_instructions = fields.Text(string='Delivery Instructions')
    x_priority_level = fields.Selection([
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical'),
    ], string='Priority', default='normal')
    x_carrier_tracking = fields.Char(string='Carrier Tracking')

    def action_done(self):
        """Override to add custom logic after validation."""
        result = super().action_done()

        for picking in self:
            if picking.picking_type_code == 'outgoing':
                picking._send_shipping_notification()

        return result

    def _send_shipping_notification(self):
        """Send notification when shipment is done."""
        template = self.env.ref('my_module.email_template_shipment')
        if self.partner_id.email:
            template.send_mail(self.id)
```

### Extend Stock Move
```python
class StockMove(models.Model):
    _inherit = 'stock.move'

    x_custom_cost = fields.Float(string='Custom Cost')
    x_batch_number = fields.Char(string='Batch Number')

    def _action_done(self, cancel_backorder=False):
        """Override to add tracking after move completion."""
        result = super()._action_done(cancel_backorder=cancel_backorder)

        for move in self:
            if move.product_id.x_min_stock_qty:
                move._check_reorder_point()

        return result

    def _check_reorder_point(self):
        """Check if reorder is needed after stock change."""
        product = self.product_id
        if product.qty_available < product.x_min_stock_qty:
            self._create_reorder_notification()
```

---

## Stock Operations

### Create Stock Move
```python
def _create_stock_move(self, product, qty, src_location, dest_location):
    """Create a stock movement."""
    move = self.env['stock.move'].create({
        'name': f'Move: {product.name}',
        'product_id': product.id,
        'product_uom_qty': qty,
        'product_uom': product.uom_id.id,
        'location_id': src_location.id,
        'location_dest_id': dest_location.id,
        'picking_type_id': self._get_picking_type().id,
        'origin': self.name,
    })
    move._action_confirm()
    move._action_assign()
    return move
```

### Create Transfer (Picking)
```python
def _create_delivery(self, partner, lines):
    """Create outgoing delivery order."""
    warehouse = self.env['stock.warehouse'].search([
        ('company_id', '=', self.env.company.id),
    ], limit=1)

    picking = self.env['stock.picking'].create({
        'partner_id': partner.id,
        'picking_type_id': warehouse.out_type_id.id,
        'location_id': warehouse.lot_stock_id.id,
        'location_dest_id': partner.property_stock_customer.id,
        'origin': self.name,
    })

    for line in lines:
        self.env['stock.move'].create({
            'name': line['product'].name,
            'product_id': line['product'].id,
            'product_uom_qty': line['qty'],
            'product_uom': line['product'].uom_id.id,
            'picking_id': picking.id,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
        })

    picking.action_confirm()
    picking.action_assign()

    return picking
```

### Internal Transfer
```python
def _create_internal_transfer(self, product, qty, src_location, dest_location):
    """Create internal transfer between locations."""
    warehouse = self.env['stock.warehouse'].search([
        ('company_id', '=', self.env.company.id),
    ], limit=1)

    picking = self.env['stock.picking'].create({
        'picking_type_id': warehouse.int_type_id.id,
        'location_id': src_location.id,
        'location_dest_id': dest_location.id,
        'origin': f'Internal Transfer: {self.name}',
    })

    self.env['stock.move'].create({
        'name': product.name,
        'product_id': product.id,
        'product_uom_qty': qty,
        'product_uom': product.uom_id.id,
        'picking_id': picking.id,
        'location_id': src_location.id,
        'location_dest_id': dest_location.id,
    })

    picking.action_confirm()
    picking.action_assign()

    return picking
```

---

## Inventory Adjustments

### Create Inventory Adjustment
```python
def _adjust_inventory(self, product, location, new_qty, reason):
    """Adjust inventory quantity for a product."""
    quant = self.env['stock.quant'].search([
        ('product_id', '=', product.id),
        ('location_id', '=', location.id),
    ], limit=1)

    current_qty = quant.quantity if quant else 0
    diff = new_qty - current_qty

    if diff == 0:
        return

    # Use inventory adjustment
    self.env['stock.quant'].with_context(inventory_mode=True).create({
        'product_id': product.id,
        'location_id': location.id,
        'inventory_quantity': new_qty,
    }).action_apply_inventory()
```

### Batch Inventory Update
```python
def _batch_inventory_adjustment(self, adjustments):
    """Process batch inventory adjustments.

    Args:
        adjustments: List of dicts with product_id, location_id, qty
    """
    for adj in adjustments:
        product = self.env['product.product'].browse(adj['product_id'])
        location = self.env['stock.location'].browse(adj['location_id'])

        quant = self.env['stock.quant'].search([
            ('product_id', '=', product.id),
            ('location_id', '=', location.id),
        ], limit=1)

        if quant:
            quant.with_context(inventory_mode=True).write({
                'inventory_quantity': adj['qty'],
            })
        else:
            self.env['stock.quant'].with_context(inventory_mode=True).create({
                'product_id': product.id,
                'location_id': location.id,
                'inventory_quantity': adj['qty'],
            })

    # Apply all adjustments
    quants_to_apply = self.env['stock.quant'].search([
        ('inventory_quantity_set', '=', True),
    ])
    quants_to_apply.action_apply_inventory()
```

---

## Stock Queries

### Get Available Quantity
```python
def _get_available_qty(self, product, location=None):
    """Get available quantity for a product."""
    if location:
        return product.with_context(location=location.id).qty_available
    return product.qty_available


def _get_free_qty(self, product, location=None):
    """Get free (unreserved) quantity."""
    if location:
        return product.with_context(location=location.id).free_qty
    return product.free_qty
```

### Get Stock by Location
```python
def _get_stock_by_location(self, product):
    """Get stock quantities per location."""
    quants = self.env['stock.quant'].search([
        ('product_id', '=', product.id),
        ('location_id.usage', '=', 'internal'),
    ])

    return {
        quant.location_id: {
            'quantity': quant.quantity,
            'reserved': quant.reserved_quantity,
            'available': quant.quantity - quant.reserved_quantity,
        }
        for quant in quants
    }
```

### Check Stock Availability
```python
def _check_stock_availability(self, lines):
    """Check if all lines can be fulfilled from stock.

    Args:
        lines: List of dicts with product_id, qty, location_id (optional)

    Returns:
        dict: {available: bool, missing: list of dicts}
    """
    missing = []

    for line in lines:
        product = self.env['product.product'].browse(line['product_id'])
        location_id = line.get('location_id')

        if location_id:
            available = product.with_context(location=location_id).free_qty
        else:
            available = product.free_qty

        if available < line['qty']:
            missing.append({
                'product': product,
                'requested': line['qty'],
                'available': available,
                'shortage': line['qty'] - available,
            })

    return {
        'available': len(missing) == 0,
        'missing': missing,
    }
```

---

## Lot and Serial Tracking

### Create with Lot
```python
def _create_move_with_lot(self, product, qty, lot_name, src_location, dest_location):
    """Create stock move with lot tracking."""
    # Ensure lot exists
    lot = self.env['stock.lot'].search([
        ('name', '=', lot_name),
        ('product_id', '=', product.id),
        ('company_id', '=', self.env.company.id),
    ], limit=1)

    if not lot:
        lot = self.env['stock.lot'].create({
            'name': lot_name,
            'product_id': product.id,
            'company_id': self.env.company.id,
        })

    move = self.env['stock.move'].create({
        'name': product.name,
        'product_id': product.id,
        'product_uom_qty': qty,
        'product_uom': product.uom_id.id,
        'location_id': src_location.id,
        'location_dest_id': dest_location.id,
    })

    move._action_confirm()
    move._action_assign()

    # Set lot on move line
    for move_line in move.move_line_ids:
        move_line.lot_id = lot

    move._action_done()
    return move
```

### Query by Lot
```python
def _get_stock_by_lot(self, product):
    """Get stock quantities per lot."""
    quants = self.env['stock.quant'].search([
        ('product_id', '=', product.id),
        ('location_id.usage', '=', 'internal'),
        ('lot_id', '!=', False),
    ])

    return {
        quant.lot_id: {
            'location': quant.location_id,
            'quantity': quant.quantity,
            'expiry_date': quant.lot_id.expiration_date,
        }
        for quant in quants
    }
```

---

## Warehouse Operations

### Get Default Warehouse
```python
def _get_warehouse(self):
    """Get warehouse for current company."""
    return self.env['stock.warehouse'].search([
        ('company_id', '=', self.env.company.id),
    ], limit=1)
```

### Get Picking Type
```python
def _get_picking_type(self, operation='outgoing'):
    """Get picking type by operation.

    Args:
        operation: 'incoming', 'outgoing', 'internal'
    """
    warehouse = self._get_warehouse()

    if operation == 'incoming':
        return warehouse.in_type_id
    elif operation == 'outgoing':
        return warehouse.out_type_id
    else:
        return warehouse.int_type_id
```

### Get Stock Locations
```python
def _get_stock_location(self):
    """Get main stock location."""
    warehouse = self._get_warehouse()
    return warehouse.lot_stock_id


def _get_customer_location(self):
    """Get customer (output) location."""
    return self.env.ref('stock.stock_location_customers')


def _get_supplier_location(self):
    """Get supplier (input) location."""
    return self.env.ref('stock.stock_location_suppliers')
```

---

## Scheduled Actions

### Low Stock Alert Cron
```python
@api.model
def _cron_check_low_stock(self):
    """Check for low stock products and send alerts."""
    low_stock_products = self.env['product.template'].search([
        ('x_min_stock_qty', '>', 0),
        ('qty_available', '<', 'x_min_stock_qty'),  # This needs SQL
    ])

    # Actually filter in Python due to comparison limitation
    products = self.env['product.template'].search([
        ('x_min_stock_qty', '>', 0),
        ('type', '=', 'product'),
    ])

    low_stock = products.filtered(
        lambda p: p.qty_available < p.x_min_stock_qty
    )

    if low_stock:
        self._send_low_stock_alert(low_stock)
```

### Auto Reorder Cron
```python
@api.model
def _cron_auto_reorder(self):
    """Automatically create purchase orders for low stock items."""
    products = self.env['product.template'].search([
        ('x_min_stock_qty', '>', 0),
        ('type', '=', 'product'),
    ])

    to_reorder = products.filtered(
        lambda p: p.qty_available < p.x_min_stock_qty
    )

    for product in to_reorder:
        self._create_reorder(product)
```

---

## Best Practices

1. **Use correct locations** - Don't hardcode location IDs
2. **Handle reservations** - Check `free_qty` not just `qty_available`
3. **Multi-company aware** - Always filter by company
4. **Lot tracking** - Enable when traceability is needed
5. **Use picking types** - Match the operation type
6. **Validate before confirm** - Check availability first
7. **Handle backorders** - Decide on backorder policy
8. **Performance** - Use `read_group` for aggregations
9. **Concurrency** - Use proper locking for inventory updates
10. **Test thoroughly** - Stock operations have many edge cases
