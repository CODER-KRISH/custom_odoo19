from odoo import fields, models, api
from odoo.exceptions import ValidationError

class purchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    s_description = fields.Char(string="Second Description")

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        res = super()._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)

        res.update({
            's_description': self.s_description
        })

        return res