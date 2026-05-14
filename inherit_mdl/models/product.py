from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    special = fields.Boolean(string="Special", help="inherited - To show the product is special")