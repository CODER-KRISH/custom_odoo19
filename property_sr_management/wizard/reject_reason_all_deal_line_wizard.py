from odoo import fields, models, api
from odoo.exceptions import ValidationError


class RejectReasonAllDealLineWizard(models.TransientModel):
    _name = 'reject.reason.all.deal.line.wizard'
    _description = 'Reject Reason For All Deals Wizard'

    property_id = fields.Many2one('property')
    offer_id = fields.Many2one('property.offer')
    reason_id = fields.Many2one('reject.reasons')

    def confirm_all_deal_reject(self):
        if not self.reason_id:
            raise ValidationError("Please select a reason")

        all_offers = self.env['property.offer'].search([
            ('property_id', '=', self.property_id.id),
            ('state', '=', 'interested')
        ])

        for offer in all_offers:
            offer.write({
                'state': 'rejected',
                'reject_reason': self.reason_id.name,
            })

        self.property_id.state = 'available'