from odoo import fields, models, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move' # This is the invoice Model

    f_description = fields.Char(string="First Description")