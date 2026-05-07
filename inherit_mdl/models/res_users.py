from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    tech_type = fields.Selection([
        ('repair', 'Repair'),
        ('installation', 'Installation'),
        ('amc', 'AMC')
    ], string="Type", default='repair')