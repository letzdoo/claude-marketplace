# Workflow and State Machine Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  WORKFLOW & STATE MACHINE PATTERNS                                           ║
║  State transitions, approvals, and business process flows                    ║
║  Use for modeling business processes with defined states and transitions     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Basic State Machine

### Simple State Field
```python
from odoo import api, fields, models
from odoo.exceptions import UserError


class MyDocument(models.Model):
    _name = 'my.document'
    _description = 'My Document'

    name = fields.Char(required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    # State transition methods
    def action_confirm(self):
        """Transition to confirmed state."""
        for record in self:
            if record.state != 'draft':
                raise UserError("Only draft documents can be confirmed.")
            record.state = 'confirmed'

    def action_done(self):
        """Transition to done state."""
        for record in self:
            if record.state != 'confirmed':
                raise UserError("Only confirmed documents can be marked done.")
            record.state = 'done'

    def action_cancel(self):
        """Cancel the document."""
        for record in self:
            if record.state == 'done':
                raise UserError("Cannot cancel completed documents.")
            record.state = 'cancel'

    def action_draft(self):
        """Reset to draft state."""
        for record in self:
            if record.state != 'cancel':
                raise UserError("Only cancelled documents can be reset to draft.")
            record.state = 'draft'
```

### View with Statusbar
```xml
<form>
    <header>
        <button name="action_confirm" string="Confirm"
                type="object" invisible="state != 'draft'"
                class="oe_highlight"/>
        <button name="action_done" string="Mark Done"
                type="object" invisible="state != 'confirmed'"
                class="oe_highlight"/>
        <button name="action_cancel" string="Cancel"
                type="object" invisible="state in ['done', 'cancel']"/>
        <button name="action_draft" string="Reset to Draft"
                type="object" invisible="state != 'cancel'"/>
        <field name="state" widget="statusbar"
               statusbar_visible="draft,confirmed,done"/>
    </header>
    <sheet>
        <group>
            <field name="name" readonly="state != 'draft'"/>
        </group>
    </sheet>
</form>
```

---

## State-Dependent Field Access

### Readonly in Certain States
```python
class MyDocument(models.Model):
    _name = 'my.document'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft')

    # These fields readonly after draft
    partner_id = fields.Many2one('res.partner')
    date = fields.Date()
    line_ids = fields.One2many('my.document.line', 'document_id')

    # Computed field for lock status
    is_locked = fields.Boolean(compute='_compute_is_locked')

    @api.depends('state')
    def _compute_is_locked(self):
        for record in self:
            record.is_locked = record.state != 'draft'
```

### View with State-Based Readonly
```xml
<form>
    <header>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <group>
            <!-- Odoo 17+ syntax -->
            <field name="partner_id" readonly="state != 'draft'"/>
            <field name="date" readonly="state != 'draft'"/>

            <!-- Or use computed field -->
            <field name="partner_id" readonly="is_locked"/>
        </group>

        <notebook>
            <page string="Lines">
                <field name="line_ids" readonly="state != 'draft'">
                    <tree editable="bottom">
                        <field name="product_id"/>
                        <field name="quantity"/>
                    </tree>
                </field>
            </page>
        </notebook>
    </sheet>
</form>
```

---

## Approval Workflow

### Multi-Level Approval
```python
class ApprovalDocument(models.Model):
    _name = 'approval.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    amount = fields.Float()

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('first_approval', 'First Approval'),
        ('second_approval', 'Second Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True)

    # Approval tracking
    submitted_by = fields.Many2one('res.users', readonly=True)
    submitted_date = fields.Datetime(readonly=True)
    first_approver_id = fields.Many2one('res.users', readonly=True)
    first_approval_date = fields.Datetime(readonly=True)
    second_approver_id = fields.Many2one('res.users', readonly=True)
    second_approval_date = fields.Datetime(readonly=True)
    rejection_reason = fields.Text()

    def action_submit(self):
        """Submit for approval."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError("Document must be in draft state.")

        self.write({
            'state': 'submitted',
            'submitted_by': self.env.uid,
            'submitted_date': fields.Datetime.now(),
        })

        # Notify approvers
        self._notify_approvers()

    def action_first_approve(self):
        """First level approval."""
        self.ensure_one()
        self._check_approval_rights('first')

        self.write({
            'state': 'first_approval',
            'first_approver_id': self.env.uid,
            'first_approval_date': fields.Datetime.now(),
        })

        # Check if second approval needed
        if self.amount > 10000:
            self._notify_second_approvers()
        else:
            self.action_final_approve()

    def action_second_approve(self):
        """Second level approval."""
        self.ensure_one()
        self._check_approval_rights('second')

        self.write({
            'state': 'second_approval',
            'second_approver_id': self.env.uid,
            'second_approval_date': fields.Datetime.now(),
        })
        self.action_final_approve()

    def action_final_approve(self):
        """Mark as fully approved."""
        self.write({'state': 'approved'})
        self._execute_approved_actions()

    def action_reject(self):
        """Reject the document."""
        self.ensure_one()
        if not self.rejection_reason:
            raise UserError("Please provide a rejection reason.")

        self.write({'state': 'rejected'})
        self._notify_rejection()

    def _check_approval_rights(self, level):
        """Verify user can approve at this level."""
        if level == 'first':
            group = 'my_module.group_first_approver'
        else:
            group = 'my_module.group_second_approver'

        if not self.env.user.has_group(group):
            raise UserError("You don't have approval rights.")

    def _notify_approvers(self):
        """Send notification to approvers."""
        # Implementation depends on notification method
        pass
```

### Approval View
```xml
<form>
    <header>
        <button name="action_submit" string="Submit for Approval"
                type="object" invisible="state != 'draft'"
                class="oe_highlight"/>
        <button name="action_first_approve" string="Approve"
                type="object" invisible="state != 'submitted'"
                class="oe_highlight"
                groups="my_module.group_first_approver"/>
        <button name="action_second_approve" string="Final Approve"
                type="object" invisible="state != 'first_approval'"
                class="oe_highlight"
                groups="my_module.group_second_approver"/>
        <button name="%(action_reject_wizard)d" string="Reject"
                type="action" invisible="state not in ['submitted', 'first_approval']"/>
        <field name="state" widget="statusbar"
               statusbar_visible="draft,submitted,first_approval,approved"/>
    </header>
    <sheet>
        <div class="oe_title">
            <h1><field name="name"/></h1>
        </div>
        <group>
            <group>
                <field name="amount"/>
            </group>
            <group>
                <field name="submitted_by" invisible="not submitted_by"/>
                <field name="submitted_date" invisible="not submitted_date"/>
                <field name="first_approver_id" invisible="not first_approver_id"/>
                <field name="second_approver_id" invisible="not second_approver_id"/>
            </group>
        </group>
        <group string="Rejection" invisible="state != 'rejected'">
            <field name="rejection_reason"/>
        </group>
    </sheet>
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="activity_ids"/>
        <field name="message_ids"/>
    </div>
</form>
```

---

## Transition Validation

### Allowed Transitions Matrix
```python
class StateMachine(models.Model):
    _name = 'state.machine'

    # Define allowed transitions
    TRANSITIONS = {
        'draft': ['submitted', 'cancel'],
        'submitted': ['approved', 'rejected', 'cancel'],
        'approved': ['done', 'cancel'],
        'rejected': ['draft'],
        'done': [],
        'cancel': ['draft'],
    }

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], default='draft')

    def _transition_to(self, new_state):
        """Safely transition to new state."""
        for record in self:
            allowed = self.TRANSITIONS.get(record.state, [])
            if new_state not in allowed:
                raise UserError(
                    f"Cannot transition from '{record.state}' to '{new_state}'. "
                    f"Allowed: {', '.join(allowed) or 'none'}"
                )
            record.state = new_state

    def action_submit(self):
        self._transition_to('submitted')

    def action_approve(self):
        self._transition_to('approved')

    def action_reject(self):
        self._transition_to('rejected')

    def action_done(self):
        self._transition_to('done')

    def action_cancel(self):
        self._transition_to('cancel')

    def action_draft(self):
        self._transition_to('draft')
```

### Transition with Pre/Post Hooks
```python
class DocumentWorkflow(models.Model):
    _name = 'document.workflow'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('done', 'Done'),
    ], default='draft')

    def _before_transition(self, from_state, to_state):
        """Hook called before state change."""
        # Validate transition is allowed
        # Check prerequisites
        pass

    def _after_transition(self, from_state, to_state):
        """Hook called after state change."""
        # Send notifications
        # Create related records
        # Update dependent fields
        pass

    def _do_transition(self, new_state):
        """Execute state transition with hooks."""
        for record in self:
            old_state = record.state
            record._before_transition(old_state, new_state)
            record.state = new_state
            record._after_transition(old_state, new_state)

    def action_start(self):
        """Start work on document."""
        for record in self:
            record._do_transition('in_progress')

    def action_submit_review(self):
        """Submit for review."""
        for record in self:
            record._do_transition('review')

    def action_complete(self):
        """Mark as complete."""
        for record in self:
            record._do_transition('done')
```

---

## Conditional State Transitions

### Amount-Based Approval
```python
class PurchaseRequest(models.Model):
    _name = 'purchase.request'

    amount_total = fields.Float()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('manager_approved', 'Manager Approved'),
        ('director_approved', 'Director Approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft')

    # Approval thresholds
    MANAGER_LIMIT = 5000
    DIRECTOR_LIMIT = 20000

    def action_submit(self):
        """Submit based on amount."""
        for record in self:
            if record.amount_total <= self.MANAGER_LIMIT:
                # Auto-approve small amounts
                record.state = 'approved'
            elif record.amount_total <= self.DIRECTOR_LIMIT:
                # Needs manager approval
                record.state = 'pending'
                record._request_manager_approval()
            else:
                # Needs director approval
                record.state = 'pending'
                record._request_director_approval()

    def action_manager_approve(self):
        """Manager approval."""
        for record in self:
            if record.amount_total <= self.DIRECTOR_LIMIT:
                record.state = 'approved'
            else:
                record.state = 'manager_approved'
                record._request_director_approval()

    def action_director_approve(self):
        """Director approval."""
        self.write({'state': 'approved'})
```

---

## Parallel States (Kanban Stages)

### Stage-Based Workflow
```python
class Task(models.Model):
    _name = 'my.task'

    name = fields.Char(required=True)

    stage_id = fields.Many2one(
        'my.task.stage',
        string='Stage',
        group_expand='_read_group_stage_ids',
        tracking=True,
        default=lambda self: self._get_default_stage(),
    )

    # Computed state from stage
    state = fields.Selection(related='stage_id.state', store=True)

    def _get_default_stage(self):
        """Get first stage."""
        return self.env['my.task.stage'].search([], limit=1)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Always show all stages in kanban."""
        return self.env['my.task.stage'].search([])


class TaskStage(models.Model):
    _name = 'my.task.stage'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string='Folded in Kanban')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], default='draft')

    is_closed = fields.Boolean(string='Closing Stage')
```

### Kanban View
```xml
<kanban default_group_by="stage_id" class="o_kanban_small_column">
    <field name="stage_id"/>
    <field name="color"/>
    <progressbar field="state"
                 colors='{"draft": "secondary", "in_progress": "warning", "done": "success"}'/>
    <templates>
        <t t-name="kanban-box">
            <div t-attf-class="oe_kanban_card oe_kanban_global_click">
                <div class="oe_kanban_content">
                    <field name="name"/>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

---

## State Change Tracking

### With Mail Thread
```python
class TrackedDocument(models.Model):
    _name = 'tracked.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)  # tracking=True logs changes

    # Custom tracking message
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
            record.message_post(
                body="Document confirmed.",
                subtype_xmlid='mail.mt_note',
            )
```

### Activity Scheduling
```python
def action_submit_for_approval(self):
    """Submit and create approval activity."""
    self.ensure_one()
    self.state = 'pending_approval'

    # Create activity for approver
    approver = self._get_approver()
    self.activity_schedule(
        'mail.mail_activity_data_todo',
        user_id=approver.id,
        summary='Approval Required',
        note=f'Please review and approve: {self.name}',
    )
```

---

## Scheduled State Transitions

### Auto-Close After Deadline
```python
class AutoCloseDocument(models.Model):
    _name = 'auto.close.document'

    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], default='active')

    expiry_date = fields.Date()

    @api.model
    def _cron_check_expiry(self):
        """Scheduled action to expire documents."""
        expired = self.search([
            ('state', '=', 'active'),
            ('expiry_date', '<', fields.Date.today()),
        ])
        expired.write({'state': 'expired'})

        # Optional: notify owners
        for doc in expired:
            doc._notify_expiry()
```

### Cron Job Definition
```xml
<record id="ir_cron_check_document_expiry" model="ir.cron">
    <field name="name">Check Document Expiry</field>
    <field name="model_id" ref="model_auto_close_document"/>
    <field name="state">code</field>
    <field name="code">model._cron_check_expiry()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
</record>
```

---

## Best Practices

1. **Use Selection for state** - Clear, finite set of states
2. **Default to 'draft'** - Start in editable state
3. **Track state changes** - Use tracking=True with mail.thread
4. **Validate transitions** - Check current state before changing
5. **Use statusbar widget** - Visual representation of progress
6. **Restrict field editing** - Lock fields in certain states
7. **Log transitions** - Keep audit trail of state changes
8. **Handle cancellation** - Always provide cancel path
9. **Reset to draft** - Allow re-processing of cancelled items
10. **Test all paths** - Verify every transition works correctly
