from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Exam(models.Model):
    _name = 'exam'
    _description = 'Exam'
    _rec_name = 'exam_rec_name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Exam Reference', default='New', copy=False, readonly=True)

    exam_name = fields.Selection([
        ('first', 'First Exam'),
        ('second', 'Second Exam'),
        ('final', 'Final Exam'),
    ], string='Exam Type', required=True)

    exam_rec_name = fields.Char(string="Exam", compute="_compute_exam_rec_name", store=True)

    @api.depends('exam_name')
    def _compute_exam_rec_name(self):
        for rec in self:
            if rec.exam_name == 'first': rec.exam_rec_name = "First Exam"
            if rec.exam_name == 'second': rec.exam_rec_name = "Second Exam"
            if rec.exam_name == 'final': rec.exam_rec_name = "Final Exam"

    standard_id = fields.Many2one('standard', string='Standard', required=True)

    academic_year = fields.Char(string='Academic Year', required=True, default=lambda self: self._get_academic_year())

    def _get_academic_year(self):
        from datetime import datetime
        year = datetime.now().year
        return f"{year}-{str(year + 1)[-2:]}"

    exam_start_date = fields.Date(string='Start Date')
    exam_end_date = fields.Date(string='End Date')

    line_ids = fields.One2many('exam.lines', 'exam_id', string='Subjects')

    total_marks = fields.Integer(string='Total Marks', compute='_compute_total_marks', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
    ], default='draft', string='Status', tracking=True)


    @api.depends('line_ids.max_marks')
    def _compute_total_marks(self):
        for rec in self:
            rec.total_marks = sum(rec.line_ids.mapped('max_marks'))

    @api.constrains('exam_start_date', 'exam_end_date')
    def _check_dates(self):
        for rec in self:
            if rec.exam_start_date and rec.exam_end_date:
                if rec.exam_end_date < rec.exam_start_date:
                    raise ValidationError('End Date cannot be before Start Date.')

    @api.constrains('passing_percentage')
    def _check_passing_percentage(self):
        for rec in self:
            if not (0 < rec.passing_percentage <= 100):
                raise ValidationError('Passing percentage must be between 1 and 100.')

    @api.onchange('standard_id')
    def _onchange_standard_id(self):
        """
            First clear old lines and append subject lines based on standard
        """


        self.line_ids = [(5, 0, 0)]
        if self.standard_id:

            subjects = self.env['subject'].search([
                ('standard_id', '=', self.standard_id.id),
                ('state', '=', 'active'),
            ])

            self.line_ids = [(0, 0, {'subject_id': subject.id}) for subject in subjects]

    @api.onchange('exam_name')
    def _onchange_exam_name(self):
        """Recompute marks on all lines when exam type changes."""
        for line in self.line_ids:
            line._compute_max_marks()

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError('Please add at least one subject before confirming.')
            if rec.name == 'New':
                rec.name = self.env['ir.sequence'].next_by_code('exam') or 'New'
            rec.state = 'confirmed'

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'