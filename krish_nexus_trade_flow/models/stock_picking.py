from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    customer_name = fields.Char(string='Customer Name', related='sale_id.partner_id.name')

    promised_delivery_date = fields.Date(string='Delivery Date', related='sale_id.promised_delivery_date')

    sale_order_number = fields.Char(string='Sale Order Number', related='sale_id.name')

    def action_notification_to_sales_person(self):

        for picking in self:

            if picking.picking_type_code != "incoming": continue

            sale_order = picking.sale_id

            if not sale_order or not sale_order.user_id: continue

            salesperson_partner = sale_order.user_id

            picking.message_post(
                body=("Goods have arrived for Sale Order <b>%s</b> for Receipt <b>%s</b>.") % (sale_order.name,
                                                                                               picking.name),
                partner_ids=[salesperson_partner.id],
                message_type="notification"
            )

        return True
