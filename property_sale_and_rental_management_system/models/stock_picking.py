from odoo import fields, models, api
from odoo.exceptions import ValidationError

class stockPicking(models.Model):

    _inherit = 'stock.picking'

    order_ids = fields.Many2many('sale.order', string='Order')

    f_description = fields.Char(string='First Description')

    def button_validate(self):
        res = super().button_validate()

        invoice = self.sale_id._create_invoices()

        invoice.action_post()

        return res
