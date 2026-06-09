from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError


class SubscriptionOrder(models.Model):
    _name = "subscription.order"
    _description = "Subscription Order Summery"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(default="New")

    user_id = fields.Many2one("res.users", tracking=True)
    account_manager_id = fields.Many2one("res.users", default=lambda self: self.env.user, string='Sales Person')

    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)

    line_ids = fields.One2many("subscription.order.line", "subscription_id", tracking=True)

    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id, tracking=True)
    amount_total = fields.Monetary(currency_field='currency_id', default=0.00, tracking=True,
                                   compute='_compute_amount_total', store=False)
    grand_total = fields.Monetary(currency_field='currency_id', default=0.00, tracking=True,
                                  compute='_compute_amount_total', store=False)
    discount = fields.Monetary(string='Discount', tracking=True, default=0.00, compute='_compute_amount_total',
                               store=False)

    state = fields.Selection([
        ("draft", "Draft"),
        ("review", "Under Review"),
        ("approved", "Approved"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', "New") == "New":
                vals['name'] = self.env['ir.sequence'].next_by_code('subscription.order') or "New"

        return super().create(vals_list)

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = 0.0
            rec.discount = 0.0
            rec.grand_total = 0.0

            amount_total = sum(rec.line_ids.mapped('subtotal'))

            rec.amount_total = amount_total

            if amount_total >= 10000:
                rec.discount = amount_total * 10 / 100

            rec.grand_total = amount_total - rec.discount

    def state_to_review(self):
        for rec in self:
            rec.state = "review"

    def state_to_approve(self):
        for rec in self:
            rec.state = "approved"