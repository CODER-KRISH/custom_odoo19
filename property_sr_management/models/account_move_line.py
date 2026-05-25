from odoo import fields, models, api
from odoo.exceptions import ValidationError

class accountMoveLine(models.Model):
    _inherit = 'account.move.line' # This is the Invoice Lines Model

    s_description = fields.Char(string="Second Description")