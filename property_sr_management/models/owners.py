from odoo import fields, models, api
from odoo.exceptions import ValidationError

class Owner(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many(
        'property',
        'owner_id',
        ondelete='cascade'
    )

    property_count = fields.Integer(string="Offers", compute="_compute_payment_count")

    def _compute_payment_count(self):
        for rec in self:
            rec.property_count = self.env['property'].search_count([
                ('owner_id', '=', rec.id)
            ])

    def action_view_all_properties(self):

        if self.property_count == 1:

            return{
                'type': 'ir.actions.act_window',
                'name': 'Properties',
                'res_model': 'property',
                'view_mode': 'form',
                'domain': [('owner_id', '=', self.id)],
                'target': 'current',
                'res_id': self.property_ids.id
            }

        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Properties',
                'res_model': 'property',
                'view_mode': 'list,form',
                'domain': [('owner_id', '=', self.id)],
                'target': 'current'
            }