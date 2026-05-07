from odoo import fields, models


class Standard(models.Model):
    _name = 'standard'
    _description = 'Standard'
    _rec_name = 'class_name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Standard Name
    class_name = fields.Char('Class Name', required=True)

    # Connects to Students
    # relation needed to add multiple students in one standard
    student_ids = fields.One2many('student', 'standard_id', string='Students')

    # Connects to Subjects
    # relation needed to add multiple subjects in one standard
    subject_ids = fields.One2many('subject', 'standard_id', string='Subjects')
