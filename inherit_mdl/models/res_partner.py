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

    def check_any_member_has_address(self):

        root = self._origin

        while root.parent_id:
            print("root......", root)
            print("root.parent_id......", root.parent_id)
            root = root.parent_id

        print("root after while loop.............", root)

        all_members = self.search([
            ('id', 'child_of', root.id),
        ]) - self._origin

        print(f"All Members are except {self._origin}.........", all_members)

        is_any_has_delivery_address = all_members.filtered(lambda l: l.is_delivery_address)
        print("is_any_has_delivery_address................", is_any_has_delivery_address)

        if is_any_has_delivery_address:
            return is_any_has_delivery_address
        else:
            return False

    @api.onchange('is_delivery_address')
    def onchange_is_delivery_address(self):

        address_found = self.check_any_member_has_address()

        if address_found:
            raise ValidationError(f"{address_found.name} has Address!")