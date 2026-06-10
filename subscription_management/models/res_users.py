from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError


class res_users(models.Model):
    _inherit = 'res.users'

    subscription_counter = fields.Integer(compute='_compute_subscription_counter')

    def _compute_subscription_counter(self):
        for rec in self:
            rec.subscription_counter = self.env['subscription.order'].search_count([
                ('user_id', '=', rec.id),
                ('state', '=', 'approved'),
            ])

    def view_subscriptions_order(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Subscription Orders',
            'res_model': 'subscription.order',
            'view_mode': 'list',
            'domain': [
                ('user_id', '=', self.id),
                ('state', '=', 'approved'),
            ],
            'target': 'current',
            'context': {
                'default_user_id': self.id,
            }
        }