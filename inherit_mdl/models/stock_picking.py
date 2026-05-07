from odoo import fields, models
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    block_delivery = fields.Boolean(string='Block Delivery', default=False, copy=False)

    def button_validate(self):
        for picking in self:
            if picking.block_delivery:
                raise UserError("Insufficient Stock!")

        return super().button_validate()