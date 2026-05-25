from odoo import fields, models, api
from odoo.exceptions import ValidationError

class PropertySaleDeal(models.Model):
    _name = 'property.sale.deal'
    _description = 'Property Sale Deal'
    _rec_name = 'property_id'
    _order = 'id desc'

    # property.agreement connects to property
    property_id = fields.Many2one('property', ondelete='cascade')

    # Payment record's Invoice Number get from payment records
    payment_reference = fields.Char("Payment Reference")

    # owner_id connects to res.users
    owner_id = fields.Many2one('res.users', string='Owner')

    # buyer_id connects to res.users
    buyer_id = fields.Many2one('res.users')

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)

    price = fields.Monetary(currency_field='currency_id')

    agreement_date = fields.Date(default=fields.Date.today)

    payment_date = fields.Datetime(string='Payment Date')

    street = fields.Char(
        string='Street',
        readonly=True,
    )
    street2 = fields.Char(
        string='Street 2',
        readonly=True,
    )
    zip = fields.Char(
        string='Zip',
        readonly=True,
    )
    city = fields.Char(
        string='City',
        readonly=True,
    )
    state_id = fields.Many2one(
        'res.country.state',
        readonly=True,
        store=True
    )
    country_id = fields.Many2one(
        'res.country',
        readonly=True,
        store=True
    )

    state = fields.Selection([
        ('payment_due', 'Payment Due'),
        ('paid', 'Paid')
    ], default='payment_due')

    def action_payment(self):
        """Method to pay Sale Agreement and create payment record"""
        """Method call when Pay button is clicked"""

        today = fields.Datetime.now()
        self.payment_date = today

        payment = self.env['property.payment.records'].create({
            'property_id': self.property_id.id,
            'buyer_id': self.buyer_id.id,
            'owner_id': self.owner_id.id,
            'property_type': self.property_id.property_type,
            'offer_price': self.price,
            'payment_date': today,
        })

        offer = self.env['property.offer'].search([
            ('property_id', '=', self.property_id.id),
            ('state', '=', 'accepted'),
        ])

        if offer:
            offer.write({
                'state' : 'closed',
            })

        self.write({
            'state': 'paid',
            'payment_reference': payment.name
        })

        self.property_id.write({
            'state': 'sold',
            'owner_id': self.buyer_id.id,
        })