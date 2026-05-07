from odoo import fields, models, api
from odoo.exceptions import ValidationError


class StudentExamLine(models.Model):
    _name = 'student.exam.line'
    _description = 'Student Exam Line'
    _order = 'id asc'

    student_exam_id = fields.Many2one('student.exam', string='Student Exam', ondelete='cascade')

    subject_id = fields.Many2one('subject', string='Subject', required=True)

    max_marks = fields.Integer(string='Max Marks', default=100)

    passing_marks = fields.Integer(string='Passing Marks', default=35)

    obtained_marks = fields.Integer(string='Marks Obtained', default=0)

    pass_or_fail = fields.Selection([
        ('p_f', 'P/F'),
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ], string='Pass/Fail', default='p_f', compute='_compute_subject_result', store=True)

    is_pass = fields.Boolean(string='Pass', compute='_compute_subject_result', store=True)

    subject_grade = fields.Char(string='Grade', compute='_compute_subject_result', store=True)

    subject_percentage = fields.Float(string='Percentage (%)', compute='_compute_subject_result', store=True)

    @api.depends('obtained_marks', 'max_marks', 'passing_marks')
    def _compute_subject_result(self):
        for rec in self:
            if rec.max_marks: pct = (rec.obtained_marks / rec.max_marks)
            else: pct = 0.0

            rec.subject_percentage = pct
            rec.is_pass = rec.obtained_marks >= rec.passing_marks

            if rec.obtained_marks == 0:
                rec.pass_or_fail = 'p_f'
            elif rec.obtained_marks >= rec.passing_marks:
                rec.pass_or_fail = 'pass'
            else:
                rec.pass_or_fail = 'fail'

            # Grade per subject
            if pct >= 90/100: rec.subject_grade = 'A+'
            elif pct >= 75/100: rec.subject_grade = 'A'
            elif pct >= 60/100: rec.subject_grade = 'B'
            elif pct >= 50/100: rec.subject_grade = 'C'
            elif pct >= 35/100: rec.subject_grade = 'D'
            elif pct != 0 and pct < 35/100: rec.subject_grade = 'F'

    @api.constrains('obtained_marks', 'max_marks')
    def _check_marks(self):
        for rec in self:
            if rec.obtained_marks < 0:
                raise ValidationError(f'Obtained marks for "{rec.subject_id.name}" cannot be negative.')
            if rec.obtained_marks > rec.max_marks:
                raise ValidationError(f'Obtained marks ({rec.obtained_marks}) for "{rec.subject_id.name}" cannot exceed maximum marks ({rec.max_marks}).')