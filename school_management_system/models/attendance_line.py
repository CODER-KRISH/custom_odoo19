from odoo import models, fields, api

class AttendanceLine(models.Model):
    _name = 'attendance.line'
    _description = 'Attendance Line'
    _rec_name = 'student_id'

    # connects to attendance model
    # relation needed because attendance.line model has 'One2many' field of attendance
    attendance_id = fields.Many2one('attendance', string='Attendance', ondelete='cascade')

    # Fetch Date from attendance model
    date = fields.Date(related='attendance_id.current_date' ,string='Date')

    # connects to standard model
    standard_id = fields.Char(related='attendance_id.standard_id.class_name', string='Standard')

    # connects to student model
    # relation needed because student model has 'One2many' field of attendance
    student_id = fields.Many2one('student', string='Student')

    status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ],default='present', string='Status')

    p_or_a = fields.Boolean(string='Present') # checkbox of present

