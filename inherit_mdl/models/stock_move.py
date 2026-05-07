from odoo import fields, models, api
from odoo.exceptions import ValidationError


class stockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        res = super()._get_new_picking_values()

        for line in self:
            if line.product_id.virtual_available < line.product_uom_qty:
                res.update({
                    'block_delivery': True
                })

        return res