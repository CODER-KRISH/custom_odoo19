from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SaleOrderConfirmWizard(models.TransientModel):

    _name = 'sale.order.confirm.wizard'

    message = fields.Char()

    def action_confirm(self):

        print("Welcome to Sale Order Confirm")
        order = self.env['sale.order'].browse(self.env.context.get('so_id'))
        order.with_context(aryan=1).action_confirm()