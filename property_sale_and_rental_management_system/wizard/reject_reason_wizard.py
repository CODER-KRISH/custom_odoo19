from odoo import fields, models, api
from odoo.exceptions import ValidationError


class RejectReasonWizard(models.TransientModel):
    _name = 'reject.reason.wizard'
    _description = 'Reject Reason wizard'

    property_id = fields.Many2one('property')
    offer_id = fields.Many2one('property.offer')
    reason_id = fields.Many2one('reject.reasons')

    def confirm_reject(self):
        if not self.reason_id:
            raise ValidationError("Please select a reason!!")
        if not self.offer_id:
            raise ValidationError("Please accept any offer!!")

        # accept selected offer
        self.offer_id.write({
            'state': 'accepted',
        })

        self.property_id.write({
            'state': 'deal_confirmed',
        })

        # find other offers for same property
        other_offers = self.env['property.offer'].search([
            ('property_id', '=', self.property_id.id),
            ('id', '!=', self.offer_id.id)
        ])

        for offer in other_offers:
            offer.write({
                'state': 'rejected',
                'reject_reason': self.reason_id.name,
            })