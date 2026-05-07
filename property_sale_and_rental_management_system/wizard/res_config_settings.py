import ast
from odoo import api, models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    category_ids = fields.Many2many('product.category', string='Categories')

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'property_sale_and_rental_management_system.category_ids',
            str(self.category_ids.ids)
        )

    @api.model
    def get_values(self):
        res = super().get_values()
        param = self.env['ir.config_parameter'].sudo().get_param(
            'property_sale_and_rental_management_system.category_ids'
        )
        if param:
            res.update({
                'category_ids': [(6, 0, ast.literal_eval(param))]
            })
        return res