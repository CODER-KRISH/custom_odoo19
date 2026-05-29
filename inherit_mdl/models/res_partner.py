from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_delivery_address = fields.Boolean(string="Delivery", default=False, copy=False)

    w_type = fields.Selection([
        ('repair', 'Repair'),
        ('installation', 'Installation'),
        ('amc', 'AMC')
    ], string="Type", default='repair')

    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.company.currency_id.id)

    used_cr_limit = fields.Monetary(string="Used Limit", currency_field='currency_id', compute='compute_credit_limits')
    left_cr_limit = fields.Monetary(string="Left Limit", currency_field='currency_id', compute='compute_credit_limits')

    @api.depends('used_cr_limit')
    def compute_credit_limits(self):

        partner_confirmed_so = self.sale_order_ids.filtered(lambda l: l.state == 'sale')
        self.used_cr_limit = sum(partner_confirmed_so.mapped('amount_total'))
        self.left_cr_limit = self.credit_limit - self.used_cr_limit

    def check_any_member_has_address(self):

        root = self._origin.commercial_partner_id

        all_members = self.search([
            ('id', 'child_of', root.id),
            ('id', '!=', self.id),
        ])

        is_any_has_delivery_address = all_members.filtered(lambda l: l.is_delivery_address)

        if is_any_has_delivery_address:
            return is_any_has_delivery_address
        else:
            return False

    @api.onchange('is_delivery_address')
    def onchange_is_delivery_address(self):

        address_found = self.check_any_member_has_address()

        if address_found:
            raise ValidationError(f"Any Member has Address!")
