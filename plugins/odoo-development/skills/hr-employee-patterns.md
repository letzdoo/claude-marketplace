# HR and Employee Patterns

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  HR & EMPLOYEE PATTERNS                                                      ║
║  Employee management, contracts, attendance, and HR workflows                ║
║  Use for HR modules, time tracking, and workforce management                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Module Setup

### Manifest Dependencies
```python
{
    'name': 'My HR Module',
    'version': '18.0.1.0.0',
    'depends': ['hr'],  # Core HR
    # Optional: 'hr_contract', 'hr_attendance', 'hr_holidays', 'hr_expense'
    'data': [
        'security/ir.model.access.csv',
        'views/hr_views.xml',
    ],
}
```

---

## Extending Employee Model

### Add Custom Fields
```python
from odoo import api, fields, models
from datetime import date
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Personal Info
    x_emergency_contact = fields.Char(string='Emergency Contact')
    x_emergency_phone = fields.Char(string='Emergency Phone')
    x_blood_type = fields.Selection([
        ('a+', 'A+'), ('a-', 'A-'),
        ('b+', 'B+'), ('b-', 'B-'),
        ('ab+', 'AB+'), ('ab-', 'AB-'),
        ('o+', 'O+'), ('o-', 'O-'),
    ], string='Blood Type')

    # Employment Info
    x_employee_number = fields.Char(
        string='Employee Number',
        copy=False,
        readonly=True,
        default='New',
    )
    x_hire_date = fields.Date(string='Hire Date')
    x_probation_end = fields.Date(
        string='Probation End Date',
        compute='_compute_probation_end',
        store=True,
    )
    x_years_of_service = fields.Float(
        string='Years of Service',
        compute='_compute_years_of_service',
    )
    x_employment_type = fields.Selection([
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contractor', 'Contractor'),
        ('intern', 'Intern'),
    ], string='Employment Type', default='full_time')

    # Skills & Certifications
    x_skill_ids = fields.Many2many(
        'hr.skill',
        string='Skills',
    )
    x_certification_ids = fields.One2many(
        'hr.employee.certification',
        'employee_id',
        string='Certifications',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('x_employee_number', 'New') == 'New':
                vals['x_employee_number'] = self.env['ir.sequence'].next_by_code(
                    'hr.employee.number'
                ) or 'New'
        return super().create(vals_list)

    @api.depends('x_hire_date')
    def _compute_probation_end(self):
        for employee in self:
            if employee.x_hire_date:
                employee.x_probation_end = employee.x_hire_date + relativedelta(months=3)
            else:
                employee.x_probation_end = False

    def _compute_years_of_service(self):
        today = date.today()
        for employee in self:
            if employee.x_hire_date:
                delta = relativedelta(today, employee.x_hire_date)
                employee.x_years_of_service = delta.years + (delta.months / 12)
            else:
                employee.x_years_of_service = 0.0
```

### Employee Certification Model
```python
class HrEmployeeCertification(models.Model):
    _name = 'hr.employee.certification'
    _description = 'Employee Certification'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(string='Certification Name', required=True)
    issuing_org = fields.Char(string='Issuing Organization')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    certificate_file = fields.Binary(string='Certificate File')
    certificate_filename = fields.Char(string='Filename')
    is_expired = fields.Boolean(
        string='Expired',
        compute='_compute_is_expired',
    )

    def _compute_is_expired(self):
        today = date.today()
        for cert in self:
            cert.is_expired = cert.expiry_date and cert.expiry_date < today
```

---

## Department Extensions

### Custom Department Fields
```python
class HrDepartment(models.Model):
    _inherit = 'hr.department'

    x_budget = fields.Monetary(
        string='Department Budget',
        currency_field='x_currency_id',
    )
    x_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    x_cost_center = fields.Char(string='Cost Center')
    x_location_id = fields.Many2one('res.partner', string='Location')

    x_employee_count = fields.Integer(
        string='Employee Count',
        compute='_compute_employee_count',
    )

    def _compute_employee_count(self):
        for dept in self:
            dept.x_employee_count = self.env['hr.employee'].search_count([
                ('department_id', '=', dept.id),
                ('active', '=', True),
            ])
```

---

## Job Positions

### Extend Job Model
```python
class HrJob(models.Model):
    _inherit = 'hr.job'

    x_min_salary = fields.Monetary(
        string='Minimum Salary',
        currency_field='x_currency_id',
    )
    x_max_salary = fields.Monetary(
        string='Maximum Salary',
        currency_field='x_currency_id',
    )
    x_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    x_required_skills = fields.Many2many(
        'hr.skill',
        string='Required Skills',
    )
    x_education_level = fields.Selection([
        ('high_school', 'High School'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD'),
    ], string='Education Required')
    x_experience_years = fields.Integer(string='Experience Required (Years)')
```

---

## Attendance Integration

### Custom Attendance Logic
```python
class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    x_location = fields.Char(string='Check-in Location')
    x_device_id = fields.Char(string='Device ID')
    x_is_remote = fields.Boolean(string='Remote Work')
    x_overtime_hours = fields.Float(
        string='Overtime Hours',
        compute='_compute_overtime',
        store=True,
    )

    @api.depends('check_in', 'check_out')
    def _compute_overtime(self):
        for attendance in self:
            if attendance.worked_hours > 8:
                attendance.x_overtime_hours = attendance.worked_hours - 8
            else:
                attendance.x_overtime_hours = 0.0


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def action_check_in(self, location=None):
        """Custom check-in with location."""
        self.ensure_one()
        return self.env['hr.attendance'].create({
            'employee_id': self.id,
            'check_in': fields.Datetime.now(),
            'x_location': location,
        })

    def action_check_out(self):
        """Custom check-out."""
        self.ensure_one()
        attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', self.id),
            ('check_out', '=', False),
        ], limit=1)

        if attendance:
            attendance.write({'check_out': fields.Datetime.now()})
            return attendance
        return False
```

---

## Leave Management

### Custom Leave Types
```python
class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    x_requires_approval = fields.Boolean(
        string='Requires Manager Approval',
        default=True,
    )
    x_max_days_per_request = fields.Integer(
        string='Max Days Per Request',
        default=0,
        help='0 = no limit',
    )
    x_requires_attachment = fields.Boolean(
        string='Requires Attachment',
        help='E.g., medical certificate for sick leave',
    )


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    x_attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments',
    )

    @api.constrains('holiday_status_id', 'number_of_days', 'x_attachment_ids')
    def _check_leave_requirements(self):
        for leave in self:
            leave_type = leave.holiday_status_id

            # Check max days
            if leave_type.x_max_days_per_request > 0:
                if leave.number_of_days > leave_type.x_max_days_per_request:
                    raise ValidationError(
                        f"Maximum {leave_type.x_max_days_per_request} days allowed per request."
                    )

            # Check attachment requirement
            if leave_type.x_requires_attachment and not leave.x_attachment_ids:
                raise ValidationError(
                    f"Attachment required for {leave_type.name}."
                )
```

---

## Employee Onboarding

### Onboarding Checklist
```python
class HrOnboardingTask(models.Model):
    _name = 'hr.onboarding.task'
    _description = 'Onboarding Task'
    _order = 'sequence, id'

    name = fields.Char(string='Task', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(default=10)
    department_id = fields.Many2one('hr.department', string='Department')
    responsible_id = fields.Many2one('res.users', string='Responsible')
    days_after_hire = fields.Integer(
        string='Days After Hire',
        help='When task should be completed',
    )
    is_mandatory = fields.Boolean(string='Mandatory', default=True)


class HrEmployeeOnboarding(models.Model):
    _name = 'hr.employee.onboarding'
    _description = 'Employee Onboarding Progress'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade',
    )
    task_id = fields.Many2one(
        'hr.onboarding.task',
        string='Task',
        required=True,
    )
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('skipped', 'Skipped'),
    ], string='Status', default='pending')
    completed_date = fields.Date(string='Completed Date')
    completed_by = fields.Many2one('res.users', string='Completed By')
    notes = fields.Text(string='Notes')

    def action_complete(self):
        self.write({
            'state': 'done',
            'completed_date': fields.Date.today(),
            'completed_by': self.env.uid,
        })


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    x_onboarding_ids = fields.One2many(
        'hr.employee.onboarding',
        'employee_id',
        string='Onboarding Tasks',
    )
    x_onboarding_progress = fields.Float(
        string='Onboarding Progress',
        compute='_compute_onboarding_progress',
    )

    def _compute_onboarding_progress(self):
        for employee in self:
            total = len(employee.x_onboarding_ids)
            done = len(employee.x_onboarding_ids.filtered(
                lambda t: t.state == 'done'
            ))
            employee.x_onboarding_progress = (done / total * 100) if total else 0

    def action_create_onboarding(self):
        """Create onboarding tasks for new employee."""
        self.ensure_one()

        # Get tasks for employee's department or general
        tasks = self.env['hr.onboarding.task'].search([
            '|',
            ('department_id', '=', self.department_id.id),
            ('department_id', '=', False),
        ])

        for task in tasks:
            self.env['hr.employee.onboarding'].create({
                'employee_id': self.id,
                'task_id': task.id,
            })

        return True
```

---

## Views

### Employee Form Extension
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_employee_form_inherit" model="ir.ui.view">
        <field name="name">hr.employee.form.inherit</field>
        <field name="model">hr.employee</field>
        <field name="inherit_id" ref="hr.view_employee_form"/>
        <field name="arch" type="xml">
            <field name="job_id" position="before">
                <field name="x_employee_number"/>
            </field>

            <xpath expr="//page[@name='public']" position="after">
                <page string="Employment" name="employment">
                    <group>
                        <group>
                            <field name="x_hire_date"/>
                            <field name="x_probation_end"/>
                            <field name="x_years_of_service"/>
                        </group>
                        <group>
                            <field name="x_employment_type"/>
                        </group>
                    </group>
                </page>
                <page string="Emergency" name="emergency">
                    <group>
                        <field name="x_emergency_contact"/>
                        <field name="x_emergency_phone"/>
                        <field name="x_blood_type"/>
                    </group>
                </page>
                <page string="Skills &amp; Certifications" name="skills">
                    <field name="x_skill_ids" widget="many2many_tags"/>
                    <field name="x_certification_ids">
                        <tree editable="bottom">
                            <field name="name"/>
                            <field name="issuing_org"/>
                            <field name="issue_date"/>
                            <field name="expiry_date"/>
                            <field name="is_expired"/>
                        </tree>
                    </field>
                </page>
            </xpath>

            <div name="button_box" position="inside">
                <button class="oe_stat_button" type="object"
                        name="action_view_onboarding"
                        icon="fa-tasks">
                    <field string="Onboarding" name="x_onboarding_progress"
                           widget="percentpie"/>
                </button>
            </div>
        </field>
    </record>
</odoo>
```

---

## Scheduled Actions

### Probation Reminder Cron
```python
@api.model
def _cron_probation_reminder(self):
    """Send reminder for employees ending probation."""
    in_7_days = date.today() + timedelta(days=7)

    employees = self.env['hr.employee'].search([
        ('x_probation_end', '=', in_7_days),
    ])

    template = self.env.ref('my_module.email_template_probation_reminder')
    for employee in employees:
        if employee.parent_id.work_email:
            template.send_mail(employee.id)
```

### Certification Expiry Alert
```python
@api.model
def _cron_certification_expiry(self):
    """Alert for expiring certifications."""
    in_30_days = date.today() + timedelta(days=30)

    expiring = self.env['hr.employee.certification'].search([
        ('expiry_date', '<=', in_30_days),
        ('expiry_date', '>=', date.today()),
    ])

    for cert in expiring:
        cert.employee_id.message_post(
            body=f"Certification '{cert.name}' expires on {cert.expiry_date}",
            message_type='notification',
        )
```

---

## Best Practices

1. **Privacy** - Use `groups="hr.group_hr_user"` for sensitive fields
2. **Employee self-service** - Separate views for employees vs HR
3. **Multi-company** - Filter employees by company
4. **Manager hierarchy** - Use `parent_id` for reporting structure
5. **Document management** - Attach contracts, certificates
6. **Activity scheduling** - Use activities for HR tasks
7. **Audit trail** - Track changes to sensitive data
8. **Integration** - Connect with payroll, expense, timesheet
