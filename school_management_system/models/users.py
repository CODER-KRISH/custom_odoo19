from odoo import fields, models

class User(models.Model):

    _inherit = 'res.users'

    student_id = fields.Many2one('student')
    teacher_id = fields.Many2one('teacher')