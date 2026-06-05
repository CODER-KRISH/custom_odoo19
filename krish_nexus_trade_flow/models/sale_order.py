from datetime import timedelta

from odoo import fields, models, api

class saleOrder(models.Model):
    _inherit = 'sale.order'

    crm_lead_id = fields.Many2one('crm.lead')

    auto_po_created = fields.Boolean(default=False, copy=False)

    promised_delivery_date = fields.Date(string='Date')

    def action_confirm(self):
        res = super().action_confirm()

        for order in self:

            vendor_products = {}

            for line in order.order_line:

                product = line.product_id

                if line.product_uom_qty <= product.virtual_available:
                    continue

                qty_to_purchase = line.product_uom_qty - product.virtual_available

                if not product.seller_ids:
                    order.message_post(body="No Vendor Found!")
                    continue

                vendor = product.seller_ids[0].partner_id
                vendor_products.setdefault(vendor.id, [])
                vendor_products[vendor.id].append({
                    'product': product,
                    'qty': qty_to_purchase,
                    'price': product.seller_ids[0].price,
                })

            for vendor_id, products in vendor_products.items():

                if order.commitment_date:
                    planned_date = order.commitment_date - timedelta(days=2)

                else:
                    planned_date = fields.Datetime.now() + timedelta(days=3)

                po = self.env['purchase.order'].create({
                    'partner_id': vendor_id,
                    'note': f'PO is auto generated from {order.name}',
                    'so_id': order.id,
                })

                for vals in products:
                    self.env['purchase.order.line'].create({
                        'order_id': po.id,
                        'product_id': vals['product'].id,
                        'name': vals['product'].display_name,
                        'product_qty': vals['qty'],
                        'price_unit': vals['price'],
                        'date_planned': planned_date,
                    })

            if vendor_products:
                order.auto_po_created = True

        return res

    def cron_action_draft_pos(self):
        """ Alert when linked po is in draft state """

        limit_date = fields.Datetime.now() - timedelta(hours=24)

        sale_orders = self.env['sale.order'].search([
            ('auto_po_created', '=', True),
            ('create_date', '<=', limit_date),
        ])

        for order in sale_orders:

            purchase_orders = self.env['purchase.order'].search([
                ('origin', '=', order.name),
                ('state', '=', 'draft'),
            ])

            if not purchase_orders:
                continue

            po_names = ", ".join(purchase_orders.mapped('name'))

            order.message_post(
                body=(
                    f"<b>Purchase Alert</b><br/>"
                    f"The following Purchase Orders are still in Draft "
                    f"more than 24 hours after automatic creation:<br/>"
                    f"{po_names}"
                ),
            )