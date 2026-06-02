from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    github_username = fields.Char(string="GitHub Username")
