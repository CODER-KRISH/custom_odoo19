from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import ValidationError


class User(models.Model):

    _inherit = 'res.users'

    student_id = fields.Many2one('student')