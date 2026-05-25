from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_new = fields.Boolean(string='Is New', copy=False)