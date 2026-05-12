from email.policy import default

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime


class StudentExam(models.Model):
    _name = 'student.exam'
    _description = 'Student Exam Result'
    _rec_name = 'exam_id'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    student_id = fields.Many2one('student', string='Student',required=True, ondelete='cascade')

    enrollment_no = fields.Char(string='Enrollment Number',related='student_id.enrollment_no',store=True)

    exam_id = fields.Many2one('exam', string='Exam',required=True, ondelete='cascade')

    exam_name = fields.Selection(related='exam_id.exam_name',store=True, string='Exam Type')

    standard_id = fields.Many2one('standard', string='Standard',related='student_id.standard_id',store=True, readonly=False)

    academic_year = fields.Char(related='exam_id.academic_year',store=True, string='Academic Year')

    line_ids = fields.One2many('student.exam.line', 'student_exam_id',string='Subject Marks')

    total_marks = fields.Integer(string='Total Marks',compute='_compute_totals', store=True)

    total_obtained_marks = fields.Integer(string='Marks Obtained',compute='_compute_totals', store=True)

    percentage = fields.Float(string='Percentage', compute='_compute_totals', store=True)

    sequence_no = fields.Char(string='Sequence Number', default='New')

    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('not_declared', 'Not Declared'),
    ], string='Result', compute='_compute_result', store=True)

    grade = fields.Char(string='Grade',compute='_compute_result', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
    ], default='draft', string='Status')

    remarks = fields.Text(string='Remarks')

    @api.depends('line_ids.obtained_marks', 'line_ids.max_marks')
    def _compute_totals(self):
        for rec in self:
            rec.total_marks = sum(rec.line_ids.mapped('max_marks'))
            rec.total_obtained_marks = sum(rec.line_ids.mapped('obtained_marks'))
            if rec.total_marks: rec.percentage = (rec.total_obtained_marks / rec.total_marks)
            else: rec.percentage = 0.0

    @api.depends('line_ids.is_pass', 'percentage', 'state')
    def _compute_result(self):
        for rec in self:

            fail_in_any_subject = rec.line_ids.filtered(lambda l: l.pass_or_fail == 'fail')
            rec.result = 'fail' if fail_in_any_subject else 'pass'

            # Grade based on percentage
            pct = rec.percentage
            if pct >= 90/100: rec.grade = 'A+'
            elif pct >= 75/100: rec.grade = 'A'
            elif pct >= 60/100: rec.grade = 'B'
            elif pct >= 50/100: rec.grade = 'C'
            elif pct >= 35/100: rec.grade = 'D'
            elif pct != 0 and pct < 35/100: rec.grade = 'F'

    @api.onchange('exam_id')
    def _onchange_exam_id(self):
        """Populate subject lines from the selected exam's subject list."""
        self.line_ids = [(5, 0, 0)]
        if self.exam_id:
            lines = []
            for subject_line in self.exam_id.line_ids:
                lines.append((0, 0, {
                    'subject_id': subject_line.subject_id.id,
                    'max_marks': subject_line.max_marks,
                    'passing_marks': subject_line.passing_marks,
                }))
            self.line_ids = lines

    @api.constrains('student_id', 'exam_id')
    def _check_unique_student_exam(self):
        for rec in self:
            duplicate = self.search([
                ('student_id', '=', rec.student_id.id),
                ('exam_id', '=', rec.exam_id.id),
                ('id', '!=', rec.id),
            ], limit=1)
            if duplicate:
                raise ValidationError(
                    f'Student "{rec.student_id.student_name}" already has a result entry for this exam.'
                )

    def action_complete_and_declare_result(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError('No subject found.')

            unfilled_obtained_marks = rec.line_ids.filtered(lambda l: l.obtained_marks <= 0)

            if unfilled_obtained_marks:
                raise ValidationError('Obtained marks cannot be negative or zero.')
            rec.state = 'done'

            if rec.sequence_no == 'New':
                today = fields.Datetime.now().strftime('%d%m%Y%H%M%S')
                rec.sequence_no = f'SR{rec.enrollment_no}{today}'

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_print_result_report(self):
            return self.env.ref('school_management_system.action_report_student_exam_result').report_action(self)