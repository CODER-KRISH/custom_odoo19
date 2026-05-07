from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ExamLines(models.Model):
    _name = 'exam.lines'
    _description = 'Exam Subject Lines'
    _rec_name = 'subject_id'
    _order = 'id asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    exam_id = fields.Many2one('exam', string='Exam', ondelete='cascade')
    exam_name = fields.Selection(related='exam_id.exam_name', string='Exam Type', store=False)
    subject_id = fields.Many2one('subject', string='Subject', required=True)
    exam_date = fields.Date(string='Exam Date')
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time')
    max_marks = fields.Integer(string='Maximum Marks', compute='_compute_max_marks', store=True)
    passing_marks = fields.Integer(string='Passing Marks', compute='_compute_passing_marks', store=True)

    @api.depends('exam_id.exam_name')
    def _compute_max_marks(self):
        """Default max marks based on exam type. Editable after creation."""
        for rec in self:
            if rec.exam_id.exam_name in ('first', 'second'): rec.max_marks = 80
            elif rec.exam_id.exam_name == 'final': rec.max_marks = 100
            else: rec.max_marks = rec.max_marks or 100

    @api.depends('exam_name')
    def _compute_passing_marks(self):
        for rec in self:
            if rec.exam_name in ('first', 'second'): rec.passing_marks = 23
            if rec.exam_name == 'final': rec.passing_marks = 30


    @api.constrains('max_marks')
    def _check_max_marks(self):
        for rec in self:
            if rec.max_marks <= 0:
                raise ValidationError(f'Maximum marks for {rec.subject_id.name} must be greater than 0.')

    @api.constrains('passing_marks', 'max_marks')
    def _check_passing_marks(self):
        for rec in self:
            if rec.passing_marks < 0:
                raise ValidationError('Passing marks cannot be negative.')
            if rec.passing_marks > rec.max_marks:
                raise ValidationError(
                    f'Passing marks ({rec.passing_marks}) cannot exceed maximum marks ({rec.max_marks}) '
                    f'for subject {rec.subject_id.name}.'
                )