# Accounting Integration Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ACCOUNTING INTEGRATION PATTERNS                                             ║
║  Journal entries, invoicing, and financial operations                        ║
║  Use for ERP integrations, financial reporting, and accounting automation    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Module Setup

### Manifest Dependencies
```python
{
    'name': 'My Accounting Module',
    'version': '18.0.1.0.0',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_data.xml',
        'views/account_views.xml',
    ],
}
```

---

## Journal Entries

### Create Journal Entry
```python
from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountingMixin(models.AbstractModel):
    _name = 'accounting.mixin'
    _description = 'Accounting Mixin'

    def _create_journal_entry(self, lines, journal=None, ref=None, date=None):
        """Create a journal entry with multiple lines.

        Args:
            lines: List of dicts with account_id, debit, credit, partner_id
            journal: account.journal record (optional)
            ref: Reference string
            date: Entry date (defaults to today)

        Returns:
            account.move record
        """
        if not journal:
            journal = self.env['account.journal'].search([
                ('type', '=', 'general'),
                ('company_id', '=', self.env.company.id),
            ], limit=1)

        move_vals = {
            'journal_id': journal.id,
            'date': date or fields.Date.today(),
            'ref': ref or self.name,
            'line_ids': [(0, 0, {
                'account_id': line['account_id'],
                'partner_id': line.get('partner_id'),
                'name': line.get('name', ref or '/'),
                'debit': line.get('debit', 0.0),
                'credit': line.get('credit', 0.0),
            }) for line in lines],
        }

        move = self.env['account.move'].create(move_vals)
        return move

    def _post_journal_entry(self, lines, **kwargs):
        """Create and post journal entry."""
        move = self._create_journal_entry(lines, **kwargs)
        move.action_post()
        return move
```

### Balanced Entry Example
```python
def _create_expense_entry(self, amount, expense_account, description):
    """Create expense journal entry."""
    bank_account = self.env['account.account'].search([
        ('account_type', '=', 'asset_cash'),
        ('company_id', '=', self.env.company.id),
    ], limit=1)

    lines = [
        {
            'account_id': expense_account.id,
            'name': description,
            'debit': amount,
            'credit': 0.0,
        },
        {
            'account_id': bank_account.id,
            'name': description,
            'debit': 0.0,
            'credit': amount,
        },
    ]

    return self._post_journal_entry(lines, ref=description)
```

---

## Invoice Creation

### Customer Invoice
```python
def _create_customer_invoice(self, partner, lines, date=None):
    """Create customer invoice.

    Args:
        partner: res.partner record
        lines: List of dicts with product_id, quantity, price_unit
        date: Invoice date

    Returns:
        account.move record (invoice)
    """
    invoice_vals = {
        'move_type': 'out_invoice',
        'partner_id': partner.id,
        'invoice_date': date or fields.Date.today(),
        'invoice_line_ids': [(0, 0, {
            'product_id': line.get('product_id'),
            'name': line.get('name', line.get('product_id') and
                           self.env['product.product'].browse(line['product_id']).name),
            'quantity': line.get('quantity', 1),
            'price_unit': line['price_unit'],
            'tax_ids': line.get('tax_ids', [(6, 0, [])]),
        }) for line in lines],
    }

    invoice = self.env['account.move'].create(invoice_vals)
    return invoice


def _create_and_post_invoice(self, partner, lines, **kwargs):
    """Create and post customer invoice."""
    invoice = self._create_customer_invoice(partner, lines, **kwargs)
    invoice.action_post()
    return invoice
```

### Vendor Bill
```python
def _create_vendor_bill(self, partner, lines, date=None, ref=None):
    """Create vendor bill.

    Args:
        partner: res.partner (vendor)
        lines: List of dicts with product_id, quantity, price_unit
        date: Bill date
        ref: Vendor reference

    Returns:
        account.move record (bill)
    """
    bill_vals = {
        'move_type': 'in_invoice',
        'partner_id': partner.id,
        'invoice_date': date or fields.Date.today(),
        'ref': ref,
        'invoice_line_ids': [(0, 0, {
            'product_id': line.get('product_id'),
            'name': line.get('name', ''),
            'quantity': line.get('quantity', 1),
            'price_unit': line['price_unit'],
        }) for line in lines],
    }

    bill = self.env['account.move'].create(bill_vals)
    return bill
```

### Credit Note
```python
def _create_credit_note(self, invoice, reason=None):
    """Create credit note for an invoice.

    Args:
        invoice: Original account.move record
        reason: Reason for credit

    Returns:
        account.move record (credit note)
    """
    # Use the reversal wizard approach
    reversal_wizard = self.env['account.move.reversal'].with_context(
        active_model='account.move',
        active_ids=invoice.ids,
    ).create({
        'reason': reason or 'Credit Note',
        'refund_method': 'refund',  # 'refund', 'cancel', 'modify'
        'journal_id': invoice.journal_id.id,
    })

    result = reversal_wizard.reverse_moves()
    credit_note = self.env['account.move'].browse(result['res_id'])

    return credit_note
```

---

## Payment Processing

### Register Payment
```python
def _register_payment(self, invoice, amount=None, date=None, journal=None):
    """Register payment for an invoice.

    Args:
        invoice: account.move record
        amount: Payment amount (defaults to invoice amount)
        date: Payment date
        journal: Payment journal

    Returns:
        account.payment record
    """
    if not journal:
        journal = self.env['account.journal'].search([
            ('type', 'in', ['bank', 'cash']),
            ('company_id', '=', self.env.company.id),
        ], limit=1)

    payment_vals = {
        'payment_type': 'inbound' if invoice.move_type == 'out_invoice' else 'outbound',
        'partner_type': 'customer' if invoice.move_type in ['out_invoice', 'out_refund'] else 'supplier',
        'partner_id': invoice.partner_id.id,
        'amount': amount or invoice.amount_residual,
        'date': date or fields.Date.today(),
        'journal_id': journal.id,
        'ref': invoice.name,
    }

    payment = self.env['account.payment'].create(payment_vals)
    payment.action_post()

    # Reconcile with invoice
    lines_to_reconcile = (payment.move_id.line_ids + invoice.line_ids).filtered(
        lambda l: l.account_id.reconcile and not l.reconciled
    )
    lines_to_reconcile.reconcile()

    return payment
```

### Bulk Payment
```python
def _create_batch_payment(self, invoices, journal=None):
    """Create batch payment for multiple invoices.

    Args:
        invoices: account.move recordset

    Returns:
        account.payment record
    """
    if not invoices:
        raise UserError("No invoices to pay")

    # Group by partner
    partner = invoices[0].partner_id
    if any(inv.partner_id != partner for inv in invoices):
        raise UserError("All invoices must be for the same partner")

    total_amount = sum(invoices.mapped('amount_residual'))

    payment = self._register_payment(
        invoices[0],
        amount=total_amount,
        journal=journal,
    )

    # Reconcile all invoices
    for invoice in invoices[1:]:
        lines_to_reconcile = (payment.move_id.line_ids + invoice.line_ids).filtered(
            lambda l: l.account_id.reconcile and not l.reconciled
        )
        lines_to_reconcile.reconcile()

    return payment
```

---

## Account Queries

### Get Account by Type
```python
def _get_account(self, account_type, company=None):
    """Get account by type.

    Args:
        account_type: e.g., 'asset_receivable', 'liability_payable',
                     'expense', 'income', 'asset_cash'
    """
    company = company or self.env.company
    return self.env['account.account'].search([
        ('account_type', '=', account_type),
        ('company_id', '=', company.id),
    ], limit=1)


def _get_receivable_account(self):
    return self._get_account('asset_receivable')


def _get_payable_account(self):
    return self._get_account('liability_payable')


def _get_expense_account(self, product=None):
    if product and product.property_account_expense_id:
        return product.property_account_expense_id
    return self._get_account('expense')


def _get_income_account(self, product=None):
    if product and product.property_account_income_id:
        return product.property_account_income_id
    return self._get_account('income')
```

### Get Journal by Type
```python
def _get_journal(self, journal_type, company=None):
    """Get journal by type.

    Args:
        journal_type: 'sale', 'purchase', 'cash', 'bank', 'general'
    """
    company = company or self.env.company
    return self.env['account.journal'].search([
        ('type', '=', journal_type),
        ('company_id', '=', company.id),
    ], limit=1)
```

---

## Financial Reports

### Partner Balance
```python
def _get_partner_balance(self, partner, account_type='asset_receivable'):
    """Get partner balance for specific account type."""
    account = self._get_account(account_type)

    self.env.cr.execute("""
        SELECT COALESCE(SUM(debit - credit), 0)
        FROM account_move_line
        WHERE partner_id = %s
        AND account_id = %s
        AND parent_state = 'posted'
    """, (partner.id, account.id))

    return self.env.cr.fetchone()[0]


def _get_customer_receivable(self, partner):
    """Get customer receivable balance."""
    return self._get_partner_balance(partner, 'asset_receivable')


def _get_vendor_payable(self, partner):
    """Get vendor payable balance."""
    return self._get_partner_balance(partner, 'liability_payable')
```

### Account Balance
```python
def _get_account_balance(self, account, date_from=None, date_to=None):
    """Get account balance for date range."""
    domain = [
        ('account_id', '=', account.id),
        ('parent_state', '=', 'posted'),
    ]

    if date_from:
        domain.append(('date', '>=', date_from))
    if date_to:
        domain.append(('date', '<=', date_to))

    lines = self.env['account.move.line'].search(domain)
    return sum(lines.mapped('balance'))
```

### Aged Receivables
```python
def _get_aged_receivables(self, partner=None):
    """Get aged receivables report data."""
    today = fields.Date.today()
    periods = [
        ('0-30', 0, 30),
        ('31-60', 31, 60),
        ('61-90', 61, 90),
        ('90+', 91, 9999),
    ]

    domain = [
        ('account_id.account_type', '=', 'asset_receivable'),
        ('parent_state', '=', 'posted'),
        ('reconciled', '=', False),
    ]

    if partner:
        domain.append(('partner_id', '=', partner.id))

    lines = self.env['account.move.line'].search(domain)

    result = {period[0]: 0.0 for period in periods}

    for line in lines:
        days = (today - line.date_maturity).days if line.date_maturity else 0
        for period_name, min_days, max_days in periods:
            if min_days <= days <= max_days:
                result[period_name] += line.amount_residual
                break

    return result
```

---

## Tax Handling

### Get Taxes
```python
def _get_sale_taxes(self, product=None):
    """Get applicable sale taxes."""
    if product:
        return product.taxes_id
    return self.env['account.tax'].search([
        ('type_tax_use', '=', 'sale'),
        ('company_id', '=', self.env.company.id),
    ])


def _get_purchase_taxes(self, product=None):
    """Get applicable purchase taxes."""
    if product:
        return product.supplier_taxes_id
    return self.env['account.tax'].search([
        ('type_tax_use', '=', 'purchase'),
        ('company_id', '=', self.env.company.id),
    ])
```

### Calculate Tax
```python
def _compute_tax_amount(self, amount, taxes, price_include=False):
    """Compute tax amount for given amount and taxes.

    Args:
        amount: Base amount
        taxes: account.tax recordset
        price_include: Whether amount includes tax

    Returns:
        dict with total, taxes breakdown
    """
    tax_results = taxes.compute_all(
        amount,
        currency=self.env.company.currency_id,
        quantity=1.0,
        product=None,
        partner=None,
        is_refund=False,
    )

    return {
        'total_included': tax_results['total_included'],
        'total_excluded': tax_results['total_excluded'],
        'taxes': tax_results['taxes'],
    }
```

---

## Reconciliation

### Auto Reconcile
```python
def _auto_reconcile_partner(self, partner):
    """Auto-reconcile partner's open items."""
    receivable_account = self._get_receivable_account()

    lines = self.env['account.move.line'].search([
        ('partner_id', '=', partner.id),
        ('account_id', '=', receivable_account.id),
        ('reconciled', '=', False),
        ('parent_state', '=', 'posted'),
    ])

    # Group by exact amount match
    by_amount = {}
    for line in lines:
        amount = abs(line.balance)
        if amount not in by_amount:
            by_amount[amount] = {'debit': [], 'credit': []}

        if line.balance > 0:
            by_amount[amount]['debit'].append(line)
        else:
            by_amount[amount]['credit'].append(line)

    # Reconcile matching amounts
    for amount, grouped in by_amount.items():
        if grouped['debit'] and grouped['credit']:
            to_reconcile = grouped['debit'][0] + grouped['credit'][0]
            to_reconcile.reconcile()
```

---

## Best Practices

1. **Always balance entries** - Debits must equal credits
2. **Use correct account types** - Receivable, payable, income, expense
3. **Post entries** - Draft entries don't affect financials
4. **Handle multi-currency** - Use currency conversion methods
5. **Respect fiscal year** - Check date restrictions
6. **Use proper journals** - Sales, purchase, bank, cash, general
7. **Reconcile regularly** - Match payments to invoices
8. **Multi-company aware** - Always filter by company
9. **Tax compliance** - Use correct tax accounts
10. **Audit trail** - Don't delete, use reversals
