from odoo import fields, models, api
from odoo.exceptions import ValidationError


class stockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id,
                               values):
        res = super()._get_stock_move_values(product_id, product_qty, product_uom, location_dest_id,
                                                            name, origin, company_id,
                                                            values)

        res.update({
            'f_description': values.get('f_description'),
            's_description': values.get('s_description')
        })

        return res
