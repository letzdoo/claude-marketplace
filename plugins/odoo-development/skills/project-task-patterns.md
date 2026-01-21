# Project and Task Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  PROJECT & TASK PATTERNS                                                     ║
║  Project management, task workflows, and time tracking                       ║
║  Use for project modules, task automation, and resource planning             ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Module Setup

### Manifest Dependencies
```python
{
    'name': 'My Project Module',
    'version': '18.0.1.0.0',
    'depends': ['project'],  # Core project
    # Optional: 'hr_timesheet', 'project_forecast', 'sale_project'
    'data': [
        'security/ir.model.access.csv',
        'views/project_views.xml',
    ],
}
```

---

## Extending Projects

### Add Custom Fields
```python
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    x_project_code = fields.Char(string='Project Code')
    x_project_type = fields.Selection([
        ('internal', 'Internal'),
        ('client', 'Client'),
        ('rd', 'R&D'),
    ], string='Project Type', default='client')
    x_budget = fields.Monetary(string='Budget', currency_field='x_currency_id')
    x_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    x_start_date = fields.Date(string='Start Date')
    x_end_date = fields.Date(string='End Date')
    x_department_id = fields.Many2one('hr.department', string='Department')
    x_project_manager_id = fields.Many2one(
        'res.users',
        string='Project Manager',
        default=lambda self: self.env.user,
    )

    # Computed fields
    x_progress = fields.Float(
        string='Progress %',
        compute='_compute_progress',
        store=True,
    )
    x_total_hours = fields.Float(
        string='Total Hours',
        compute='_compute_hours',
    )
    x_remaining_budget = fields.Monetary(
        string='Remaining Budget',
        compute='_compute_remaining_budget',
        currency_field='x_currency_id',
    )

    @api.depends('task_ids.stage_id', 'task_ids.x_progress')
    def _compute_progress(self):
        for project in self:
            tasks = project.task_ids.filtered(lambda t: t.active)
            if tasks:
                project.x_progress = sum(tasks.mapped('x_progress')) / len(tasks)
            else:
                project.x_progress = 0.0

    def _compute_hours(self):
        for project in self:
            project.x_total_hours = sum(
                project.task_ids.mapped('effective_hours')
            )

    def _compute_remaining_budget(self):
        for project in self:
            spent = sum(project.task_ids.mapped('x_cost'))
            project.x_remaining_budget = project.x_budget - spent
```

### Project Stages
```python
class ProjectProjectStage(models.Model):
    _name = 'project.project.stage'
    _description = 'Project Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string='Folded in Kanban')
    description = fields.Text(string='Description')


class ProjectProject(models.Model):
    _inherit = 'project.project'

    x_stage_id = fields.Many2one(
        'project.project.stage',
        string='Stage',
        tracking=True,
        group_expand='_read_group_stage_ids',
    )

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Show all stages in kanban."""
        return stages.search([], order=order)
```

---

## Extending Tasks

### Add Custom Fields
```python
class ProjectTask(models.Model):
    _inherit = 'project.task'

    x_task_type = fields.Selection([
        ('feature', 'Feature'),
        ('bug', 'Bug Fix'),
        ('improvement', 'Improvement'),
        ('support', 'Support'),
    ], string='Task Type', default='feature')
    x_priority_level = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical'),
    ], string='Priority Level', default='1')
    x_estimated_hours = fields.Float(string='Estimated Hours')
    x_progress = fields.Float(
        string='Progress %',
        compute='_compute_progress',
        store=True,
    )
    x_cost = fields.Monetary(
        string='Cost',
        compute='_compute_cost',
        currency_field='x_currency_id',
    )
    x_currency_id = fields.Many2one(
        related='project_id.x_currency_id',
    )
    x_reviewer_id = fields.Many2one('res.users', string='Reviewer')
    x_due_warning = fields.Boolean(
        string='Due Warning',
        compute='_compute_due_warning',
    )

    @api.depends('effective_hours', 'x_estimated_hours')
    def _compute_progress(self):
        for task in self:
            if task.x_estimated_hours:
                progress = (task.effective_hours / task.x_estimated_hours) * 100
                task.x_progress = min(progress, 100)
            else:
                task.x_progress = 0.0

    def _compute_cost(self):
        for task in self:
            # Calculate cost from timesheets
            cost = sum(
                ts.unit_amount * ts.employee_id.hourly_cost
                for ts in task.timesheet_ids
            )
            task.x_cost = cost

    @api.depends('date_deadline')
    def _compute_due_warning(self):
        today = fields.Date.today()
        warning_days = 3
        for task in self:
            if task.date_deadline:
                days_until = (task.date_deadline - today).days
                task.x_due_warning = 0 <= days_until <= warning_days
            else:
                task.x_due_warning = False
```

### Task Dependencies
```python
class ProjectTask(models.Model):
    _inherit = 'project.task'

    x_depends_on_ids = fields.Many2many(
        'project.task',
        'project_task_dependency_rel',
        'task_id',
        'depends_on_id',
        string='Depends On',
    )
    x_blocking_ids = fields.Many2many(
        'project.task',
        'project_task_dependency_rel',
        'depends_on_id',
        'task_id',
        string='Blocking',
    )
    x_is_blocked = fields.Boolean(
        string='Is Blocked',
        compute='_compute_is_blocked',
    )

    @api.depends('x_depends_on_ids.stage_id')
    def _compute_is_blocked(self):
        done_stages = self.env['project.task.type'].search([
            ('fold', '=', True),
        ])
        for task in self:
            blocking = task.x_depends_on_ids.filtered(
                lambda t: t.stage_id not in done_stages
            )
            task.x_is_blocked = bool(blocking)

    @api.constrains('x_depends_on_ids')
    def _check_circular_dependency(self):
        for task in self:
            if task in task._get_all_dependencies():
                raise ValidationError("Circular dependency detected!")

    def _get_all_dependencies(self, visited=None):
        """Recursively get all dependencies."""
        if visited is None:
            visited = set()
        dependencies = self.env['project.task']
        for dep in self.x_depends_on_ids:
            if dep.id not in visited:
                visited.add(dep.id)
                dependencies |= dep
                dependencies |= dep._get_all_dependencies(visited)
        return dependencies
```

### Task Checklists
```python
class ProjectTaskChecklist(models.Model):
    _name = 'project.task.checklist'
    _description = 'Task Checklist Item'
    _order = 'sequence, id'

    task_id = fields.Many2one(
        'project.task',
        string='Task',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(string='Item', required=True)
    sequence = fields.Integer(default=10)
    is_done = fields.Boolean(string='Done')
    done_date = fields.Datetime(string='Done Date')
    done_by = fields.Many2one('res.users', string='Done By')

    def action_toggle_done(self):
        for item in self:
            if item.is_done:
                item.write({
                    'is_done': False,
                    'done_date': False,
                    'done_by': False,
                })
            else:
                item.write({
                    'is_done': True,
                    'done_date': fields.Datetime.now(),
                    'done_by': self.env.uid,
                })


class ProjectTask(models.Model):
    _inherit = 'project.task'

    x_checklist_ids = fields.One2many(
        'project.task.checklist',
        'task_id',
        string='Checklist',
    )
    x_checklist_progress = fields.Float(
        string='Checklist Progress',
        compute='_compute_checklist_progress',
    )

    @api.depends('x_checklist_ids.is_done')
    def _compute_checklist_progress(self):
        for task in self:
            total = len(task.x_checklist_ids)
            done = len(task.x_checklist_ids.filtered('is_done'))
            task.x_checklist_progress = (done / total * 100) if total else 0
```

---

## Task Automation

### Auto-Assignment
```python
class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        for task in tasks:
            if not task.user_ids and task.project_id.x_project_manager_id:
                task.user_ids = task.project_id.x_project_manager_id
        return tasks

    def write(self, vals):
        result = super().write(vals)

        # Auto-assign reviewer when task moves to review stage
        if 'stage_id' in vals:
            review_stage = self.env.ref('my_module.task_stage_review', raise_if_not_found=False)
            if review_stage and self.stage_id == review_stage:
                if not self.x_reviewer_id:
                    self.x_reviewer_id = self.project_id.x_project_manager_id

        return result
```

### Stage Change Notifications
```python
class ProjectTask(models.Model):
    _inherit = 'project.task'

    def write(self, vals):
        old_stages = {task.id: task.stage_id for task in self}
        result = super().write(vals)

        if 'stage_id' in vals:
            for task in self:
                old_stage = old_stages.get(task.id)
                if old_stage != task.stage_id:
                    task._notify_stage_change(old_stage)

        return result

    def _notify_stage_change(self, old_stage):
        """Send notification on stage change."""
        self.message_post(
            body=f"Stage changed from '{old_stage.name}' to '{self.stage_id.name}'",
            message_type='notification',
        )

        # Notify assignees
        for user in self.user_ids:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=f'Task moved to {self.stage_id.name}',
                user_id=user.id,
            )
```

---

## Views

### Project Form Extension
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_project_form_inherit" model="ir.ui.view">
        <field name="name">project.project.form.inherit</field>
        <field name="model">project.project</field>
        <field name="inherit_id" ref="project.edit_project"/>
        <field name="arch" type="xml">
            <field name="partner_id" position="after">
                <field name="x_project_code"/>
                <field name="x_project_type"/>
            </field>

            <xpath expr="//page[@name='settings']" position="before">
                <page string="Planning" name="planning">
                    <group>
                        <group>
                            <field name="x_start_date"/>
                            <field name="x_end_date"/>
                            <field name="x_department_id"/>
                        </group>
                        <group>
                            <field name="x_budget"/>
                            <field name="x_remaining_budget"/>
                            <field name="x_progress" widget="progressbar"/>
                        </group>
                    </group>
                </page>
            </xpath>
        </field>
    </record>
</odoo>
```

### Task Form Extension
```xml
<record id="view_task_form_inherit" model="ir.ui.view">
    <field name="name">project.task.form.inherit</field>
    <field name="model">project.task</field>
    <field name="inherit_id" ref="project.view_task_form2"/>
    <field name="arch" type="xml">
        <field name="priority" position="after">
            <field name="x_task_type"/>
            <field name="x_priority_level"/>
        </field>

        <field name="user_ids" position="after">
            <field name="x_reviewer_id"/>
        </field>

        <xpath expr="//page[@name='description_page']" position="after">
            <page string="Planning" name="planning">
                <group>
                    <group>
                        <field name="x_estimated_hours"/>
                        <field name="effective_hours"/>
                        <field name="x_progress" widget="progressbar"/>
                    </group>
                    <group>
                        <field name="x_depends_on_ids" widget="many2many_tags"/>
                        <field name="x_is_blocked"/>
                    </group>
                </group>
            </page>
            <page string="Checklist" name="checklist">
                <field name="x_checklist_ids">
                    <tree editable="bottom">
                        <field name="sequence" widget="handle"/>
                        <field name="name"/>
                        <field name="is_done"/>
                        <field name="done_by" readonly="1"/>
                        <field name="done_date" readonly="1"/>
                    </tree>
                </field>
                <field name="x_checklist_progress" widget="progressbar"/>
            </page>
        </xpath>
    </field>
</record>
```

---

## Scheduled Actions

### Overdue Task Alerts
```python
@api.model
def _cron_check_overdue_tasks(self):
    """Alert on overdue tasks."""
    today = fields.Date.today()
    overdue_tasks = self.env['project.task'].search([
        ('date_deadline', '<', today),
        ('stage_id.fold', '=', False),  # Not done
    ])

    for task in overdue_tasks:
        task.message_post(
            body="This task is overdue!",
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
        )

        # Notify manager
        if task.project_id.x_project_manager_id:
            task.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=f'Overdue task: {task.name}',
                user_id=task.project_id.x_project_manager_id.id,
            )
```

---

## Best Practices

1. **Use stages** for workflow, not custom fields
2. **Track dependencies** for complex projects
3. **Time tracking** - integrate with hr_timesheet
4. **Progress calculation** - automate based on subtasks/checklists
5. **Notifications** - notify on stage changes and deadlines
6. **Budget tracking** - link costs to timesheets
7. **Hierarchy** - use parent tasks for organization
8. **Templates** - create project templates for recurring types
9. **Access rights** - control visibility by project
10. **Reporting** - track velocity, burndown, etc.
