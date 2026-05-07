from odoo import fields, models, api
from odoo.exceptions import ValidationError

class saleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    name_id = fields.Many2one('sale.order.info', string='Name')

    s_description = fields.Char(string="Second Description")

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()

        res.update({
            's_description': self.s_description,
            'f_description': self.order_id.f_description
        })

        return res

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)

        res.update({
            's_description': self.s_description
        })

        return res