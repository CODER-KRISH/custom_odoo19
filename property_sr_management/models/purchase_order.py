from odoo import fields, models, api
from odoo.exceptions import ValidationError

class purchaseOrder(models.Model):
    _inherit = 'purchase.order'

    f_description = fields.Char(string="First Description")

    def _prepare_picking(self):

        res = super()._prepare_picking()

        res.update({
            'f_description': self.f_description
        })

        return res