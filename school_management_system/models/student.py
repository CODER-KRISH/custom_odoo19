from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import AccessError, ValidationError


class Student(models.Model):
    _name = 'student'
    _description = 'Description of Student'
    _rec_name = 'user_id'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    admission_id = fields.Many2one('admission', string='Admission', ondelete='cascade')
    student_name = fields.Char(string='Name', required=True)
    user_id = fields.Many2one('res.users')
    image = fields.Binary(string='Image')
    phone = fields.Char(readonly=False, string="Phone")
    email = fields.Char(readonly=False, string="Email")
    current_date = fields.Date('Admission Date', default=fields.Datetime.today(), readonly=True)
    enrollment_no = fields.Char('Enrollment No:')

    dob = fields.Date('Date of Birth')
    age = fields.Integer('Age', compute='_compute_age', store=True)

    @api.depends('dob')
    def _compute_age(self):
        """ Compute Method for Age from dob """
        for rec in self:
            if rec.dob:
                rec.age = datetime.now().year - rec.dob.year

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])

    state = fields.Selection([
        ('admission_confirm', 'Confirmed'),
        ('in_admission', 'In Admission'),
        ('terminate', 'Terminated')
    ])

    street = fields.Char(readonly=False)
    street2 = fields.Char(readonly=False)
    zip = fields.Char(readonly=False)
    city = fields.Char(readonly=False)
    state_id = fields.Many2one('res.country.state', string="State", readonly=True)
    country_id = fields.Many2one('res.country', string="Country", readonly=True)

    standard_id = fields.Many2one('standard', string='Standard')
    hobby_ids = fields.Many2many('hobby', 'student_hobby_rel', 'student_id', 'hobby_id', string='Hobby')
    exam_ids = fields.Many2many('exam', 'exam_student_rel', 'student_id', 'exam_id', string="Exams")
    attendance_line_ids = fields.One2many('attendance.line', 'student_id', string="Attendance Lines")
    fees_ids = fields.One2many('student.fees.payment', 'student_id')
    all_exam_ids = fields.One2many('student.exam', 'student_id', ondelete="cascade")

    """Smart Button Logic for Student Fees"""

    student_fee_count = fields.Integer(string="Fees", compute='_compute_fees')

    def _compute_fees(self):
        for rec in self:
            rec.student_fee_count = self.env['student.fees.payment'].search_count([
                ('student_id', '=', rec.user_id.student_id.id),
            ])

    def action_view_fee_payments(self):

        domain = [('student_id', '=', self.user_id.student_id.id)]

        action = {
            'type': 'ir.actions.act_window',
            'name': 'Student Fees',
            'res_model': 'student.fees.payment',
            'view_mode': "list",
            'views': [(False, "list"), (False, "form")],
            'domain': domain,
        }

        if len(self.fees_ids) == 1:
            action.update({
                "views": [(False, "form")],
                "res_id": self.fees_ids.id
            })

        return action

    """Smart Button Logic for Student Exam Result Count"""

    student_exam_count = fields.Integer(string="Exams", compute='_compute_exams')

    def _compute_exams(self):
        for rec in self:
            rec.student_exam_count = self.env['student.exam'].search_count([
                ('student_id', '=', rec.user_id.student_id.id),
            ])

    def action_view_exam(self):
        domain = [('student_id', '=', self.user_id.student_id.id)]

        action = {
            'type': 'ir.actions.act_window',
            'name': 'Student Exam',
            'res_model': 'student.exam',
            'view_mode': "list",
            'views': [(False, "list"), (False, "form")],
            'domain': domain,
        }

        if len(self.all_exam_ids) == 1:
            action.update({
                "views": [(False, "form")],
                "res_id": self.all_exam_ids.id
            })

        return action


    """Smart Button Logic of student Attendance Counts"""

    student_attendance_count = fields.Integer(string="Attendance", compute='_compute_attendance')

    def _compute_attendance(self):
        for rec in self:
            rec.student_attendance_count = self.env['attendance.line'].search_count([
                ('student_id', '=', rec.user_id.student_id.id),
            ])

    def action_view_attendance(self):
        domain = [('student_id', '=', self.user_id.student_id.id)]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Student Exam',
            'res_model': 'attendance.line',
            'view_mode': "list",
            'domain': domain,
        }