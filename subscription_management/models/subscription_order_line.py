from odoo import fields, models, api

class ResourceSubscriptionLine(models.Model):
    _name = "subscription.order.line"
    _description = "Subscription Order Line"
    _rec_name = 'product_id'

    subscription_id = fields.Many2one("subscription.order", ondelete="cascade")

    product_id = fields.Many2one("product.product", string='Product', tracking=True)

    quantity = fields.Integer(string="Qty", default=1)
    price_unit = fields.Float(string="Unit Price", related="product_id.list_price")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    subtotal = fields.Monetary(string='Total', currency_field='currency_id', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit', 'product_id')
    def _compute_subtotal(self):
        for rec in self:
            if rec.quantity and rec.price_unit:
                rec.subtotal = rec.quantity * rec.price_unit
