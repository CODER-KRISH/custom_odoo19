from email.policy import default

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class TimetableLineMixin(models.AbstractModel):

    _name = 'timetable.line.mixin'
    _description = 'Timetable Line Mixin'
    _order = 'start_time asc'

    timetable_id = fields.Many2one(
        'timetable', string='Timetable', ondelete='cascade', required=True, tracking=True
    )

    # period_no = fields.Integer(string='Period No.', required=True)

    subject_id = fields.Many2one('subject', string='Subject', required=True, tracking=True)
    teacher_id = fields.Many2one('teacher', string='Teacher', tracking=True)
    start_time = fields.Float(string='Start Time', required=True, tracking=True)
    end_time = fields.Float(string='End Time', required=True, tracking=True)

    duration = fields.Float(
        string='Duration (hrs)', compute='_compute_duration', store=True, tracking=True
    )

    period_type = fields.Selection([
        ('lecture', 'Lecture'),
        ('practical', 'Practical'),
        ('break', 'Break'),
        ('activity', 'Activity'),
    ], string='Period Type', default='lecture', required=True, tracking=True)

    room = fields.Char(string='Room / Classroom')
    notes = fields.Char(string='Notes')

    # ── Computed ───────────────────────────────────────────────────────────

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for rec in self:
            rec.duration = max(rec.end_time - rec.start_time, 0.0)

    # ── Constraints ────────────────────────────────────────────────────────

    @api.constrains('start_time', 'end_time')
    def _check_times(self):
        for rec in self:
            if rec.start_time < 0 or rec.end_time < 0:
                raise ValidationError('Time values cannot be negative.')
            if rec.end_time <= rec.start_time:
                raise ValidationError(
                    f'End time must be after start time for '
                )

    @api.constrains('timetable_id', 'start_time', 'end_time', 'teacher_id')
    def _check_teacher_overlap(self):
        """Prevent the same teacher from being double-booked on the same day."""
        for rec in self:
            if not rec.teacher_id:
                continue
            overlaps = self.search([
                ('timetable_id', '=', rec.timetable_id.id),
                ('teacher_id', '=', rec.teacher_id.id),
                ('id', '!=', rec.id),
            ])
            for other in overlaps:
                if not (rec.end_time <= other.start_time or rec.start_time >= other.end_time):
                    raise ValidationError(
                        f'Teacher "{rec.teacher_id.user_id.name}" has an overlapping '
                    )

# ──────────────────────────────────────────────────────────────────────────────
# Six concrete day models  (one DB table each)
# ──────────────────────────────────────────────────────────────────────────────

class TimetableMonday(models.Model):
    _name = 'timetable.monday'
    _description = 'Timetable – Monday'
    _inherit = 'timetable.line.mixin'


class TimetableTuesday(models.Model):
    _name = 'timetable.tuesday'
    _description = 'Timetable – Tuesday'
    _inherit = 'timetable.line.mixin'


class TimetableWednesday(models.Model):
    _name = 'timetable.wednesday'
    _description = 'Timetable – Wednesday'
    _inherit = 'timetable.line.mixin'


class TimetableThursday(models.Model):
    _name = 'timetable.thursday'
    _description = 'Timetable – Thursday'
    _inherit = 'timetable.line.mixin'


class TimetableFriday(models.Model):
    _name = 'timetable.friday'
    _description = 'Timetable – Friday'
    _inherit = 'timetable.line.mixin'


class TimetableSaturday(models.Model):
    _name = 'timetable.saturday'
    _description = 'Timetable – Saturday'
    _inherit = 'timetable.line.mixin'

# Main Time Table

class Timetable(models.Model):
    _name = 'timetable'
    _description = 'Class Timetable'
    _rec_name = 'name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Timetable Reference',
        default='New',
        copy=False,
        readonly=True,
        tracking=True
    )

    standard_id = fields.Many2one('standard', string='Standard', required=True, tracking=True)

    academic_year = fields.Char(
        string='Academic Year',
        required=True,
        default=lambda self: self._get_academic_year(), tracking=True
    )

    created_date = fields.Date(default=fields.Date.today, string="Created", tracking=True)

    updated_date = fields.Datetime(default=fields.Datetime.now(), string="Updated", tracking=True)

    def _get_academic_year(self):
        from datetime import datetime
        year = datetime.now().year
        return f"{year}-{str(year + 1)[-2:]}"

    effective_from = fields.Date(string='Effective From', required=True)
    effective_to = fields.Date(string='Effective To')

    # ── Per-day One2many relations ─────────────────────────────────────────

    monday_ids = fields.One2many('timetable.monday', 'timetable_id', string='Monday', tracking=True)
    tuesday_ids = fields.One2many('timetable.tuesday', 'timetable_id', string='Tuesday', tracking=True)
    wednesday_ids = fields.One2many('timetable.wednesday', 'timetable_id', string='Wednesday', tracking=True)
    thursday_ids = fields.One2many('timetable.thursday', 'timetable_id', string='Thursday', tracking=True)
    friday_ids = fields.One2many('timetable.friday', 'timetable_id', string='Friday', tracking=True)
    saturday_ids = fields.One2many('timetable.saturday', 'timetable_id', string='Saturday', tracking=True)

    # ── Summary ───────────────────────────────────────────────────────────

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='Status', tracking=True)

    notes = fields.Text(string='Notes')

    # ── Constraints ───────────────────────────────────────────────────────

    @api.constrains('effective_from', 'effective_to')
    def _check_dates(self):
        for rec in self:
            if rec.effective_from and rec.effective_to:
                if rec.effective_to < rec.effective_from:
                    raise ValidationError('Effective To cannot be before Effective From.')

    @api.constrains('standard_id', 'academic_year', 'state')
    def _check_unique_confirmed(self):
        for rec in self:
            if rec.state == 'confirmed':
                duplicate = self.search([
                    ('standard_id', '=', rec.standard_id.id),
                    ('academic_year', '=', rec.academic_year),
                    ('state', '=', 'confirmed'),
                    ('id', '!=', rec.id),
                ], limit=1)
                if duplicate:
                    raise ValidationError(
                        f'A confirmed timetable already exists for '
                        f'{rec.standard_id.class_name} – {rec.academic_year}.'
                    )

    # ── Onchange ──────────────────────────────────────────────────────────

    @api.onchange('standard_id')
    def _onchange_standard_id(self):
        """Clear all day lines when standard changes."""
        self.monday_ids = [(5, 0, 0)]
        self.tuesday_ids = [(5, 0, 0)]
        self.wednesday_ids = [(5, 0, 0)]
        self.thursday_ids = [(5, 0, 0)]
        self.friday_ids = [(5, 0, 0)]
        self.saturday_ids = [(5, 0, 0)]

    # ── Actions ───────────────────────────────────────────────────────────

    def action_confirm(self):
        for rec in self:
            has_any = any([
                rec.monday_ids, rec.tuesday_ids, rec.wednesday_ids,
                rec.thursday_ids, rec.friday_ids, rec.saturday_ids,
            ])
            if not has_any:
                raise ValidationError('Please add at least one period before confirming.')
            if rec.name == 'New':
                rec.name = self.env['ir.sequence'].next_by_code('timetable') or 'New'
            rec.state = 'confirmed'
            rec.updated_date = fields.Datetime.now()

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'