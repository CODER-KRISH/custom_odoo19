from odoo import fields, models, api

class purchaseOrder(models.Model):

    _inherit = 'purchase.order'

    so_id = fields.Many2one('sale.order')

    def _prepare_picking(self):

        res = super()._prepare_picking()

        res.update({
            'customer_name': self.so_id.partner_id.name,
            'promised_delivery_date': self.so_id.promised_delivery_date,
            'sale_order_number': self.so_id.name
        })

        return res