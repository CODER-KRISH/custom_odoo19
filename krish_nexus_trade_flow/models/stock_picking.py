from odoo import fields, models, api

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    customer_name = fields.Char(string='Customer Name', related='sale_id.partner_id.name')

    promised_delivery_date = fields.Date(string='Delivery Date', related='sale_id.promised_delivery_date')

    sale_order_number = fields.Char(string='Sale Order Number', related='sale_id.name')