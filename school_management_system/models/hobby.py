from odoo import fields, models


class Hobby(models.Model):
    _name = 'hobby'
    _description = 'Description of Hobbies'
    _rec_name = 'hobbies_name'
    _order = 'id desc'

    # hobbies name
    hobbies_name = fields.Char('Hobby')

    # relation needed to show multiple students in one hobby
    student_ids = fields.Many2many('student', 'student_hobby_rel', 'hobby_id', 'student_id',  string='Student')