from email.policy import default

from odoo import models, fields, api


class Attendance(models.Model):
    _name = 'attendance'
    _description = 'Attendance'
    _rec_name = 'current_date'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Show current date
    current_date = fields.Date('Current Date', required=True, default=fields.Date.today)

    # attendance connects to standard for attendance
    # relation needed to select anyone standard for attendance
    standard_id = fields.Many2one('standard', string='Standard')

    # attendance model connects to attendance.line to show the entire object in this model
    attendance_line_ids = fields.One2many('attendance.line', 'attendance_id', string='Attendance Lines')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
    ], default='draft', string='Status')

    @api.onchange('standard_id')
    def _onchange_standard(self):

        # Clear Old attendance lines
        self.attendance_line_ids = [(5, 0, 0)]

        if self.standard_id:
            lines = []

            students = self.env['student'].search([
                ('standard_id', '=', self.standard_id.id)
            ])

            for stu in students:
                lines.append((0, 0, {
                    'student_id': stu.id
                }))

            self.attendance_line_ids = lines

    def done_attendance(self):
        for rec in self:
            rec.write({'state': 'done'})

    def set_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})