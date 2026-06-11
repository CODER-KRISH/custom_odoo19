from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError
from openpyxl.worksheet import related


class SubscriptionOrder(models.Model):
    _name = "subscription.order"
    _description = "Subscription Order Summery"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(default="New", copy=False)

    partner_id = fields.Many2one("res.partner", tracking=True)
    account_manager_id = fields.Many2one("res.partner", default=lambda self: self.env.user, string='Sales Person')
    color = fields.Integer(string='Color')
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

    payment_term_id = fields.Many2one("account.payment.term", related='partner_id.property_payment_term_id',
                                      tracking=True, store=True)

    mail_sent = fields.Boolean(default=False, copy=False)

    street = fields.Char(related='partner_id.street', store=True)
    street2 = fields.Char(related='partner_id.street2', store=True)
    city = fields.Char(related='partner_id.city', store=True)
    state_id = fields.Many2one('res.country.state', related='partner_id.state_id', store=True)
    zip = fields.Char(related='partner_id.zip', store=True)
    country_id = fields.Many2one('res.country', related='partner_id.country_id', store=True)

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
            if not rec.line_ids:
                raise ValidationError("Cannot review this order without any lines!")
            rec.state = "review"

    def state_to_approve(self):
        for rec in self:
            has_overlap = False

            for line in rec.line_ids:
                if not line.product_id:
                    continue

                overlapping_subscription = self.search([
                    ('id', '!=', rec.id),
                    ('state', '=', 'approved'),
                    ('line_ids.product_id', '=', line.product_id.id),
                    ('start_date', '<=', rec.end_date),
                    ('end_date', '>=', rec.start_date),
                ], limit=1)

                if overlapping_subscription:
                    has_overlap = True
                    break

            if has_overlap:
                rec.state = 'cancelled'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': 'Another subscription already exists with the same product in the selected date range.',
                        'type': 'danger',
                        'sticky': False,
                    }
                }
            else: rec.state = 'approved'

    def action_cron_review_orders(self):
        today = fields.Date.today()

        expiry_orders = self.search([
            ('state', '=', 'approved'),
            ('end_date', '=', today),
        ])

        template = self.env.ref(
            'subscription_management.mail_template_subscription_expiry',
            raise_if_not_found=False
        )

        for order in expiry_orders:
            if template and not order.mail_sent:

                template.send_mail(order.id, force_send=True)
                order.mail_sent = True

            order.state = "expired"

    def unlink(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError("Only Draft State Orders can be deleted!")
        return super().unlink()

    def print_order_receipt(self):
        return self.env.ref('subscription_management.action_report_order_receipt').report_action(self)

    def state_to_draft(self):
        for rec in self:
            rec.state = "draft"