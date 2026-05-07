from odoo import fields, models, api
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError


class Property(models.Model):
    _name = 'property'
    _description = 'Property'
    _order = 'id desc'

    name = fields.Char(
        'Property Name',
        required=True
    )

    property_type = fields.Selection([
        ('sale', 'For Sale'),
        ('rent', 'For Rent')
    ], required=True)

    owner_id = fields.Many2one(
        'res.users',
        string='Owner',
        required=True,
        ondelete='cascade'
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )

    sale_price = fields.Monetary(
        string="Offer Price",
        currency_field='currency_id'
    )

    rent_price = fields.Monetary(
        string="Rent Amount",
        currency_field='currency_id'
    )

    amount = fields.Monetary(
        string="Amount",
        currency_field='currency_id',
        compute="_compute_amount",
        store=True
    )

    """
        Compute Method for label of price
        if sale then label is sale Price
        if Rent then label is rent amount
    """

    @api.depends('property_type', 'sale_price', 'rent_price')
    def _compute_amount(self):
        for rec in self:
            if rec.property_type == 'sale':
                rec.amount = rec.sale_price
            if rec.property_type == 'rent':
                rec.amount = rec.rent_price

    street = fields.Char(
        string='Street'
    )
    street2 = fields.Char(
        string='Street 2'
    )
    zip = fields.Char(
        string='Zip'
    )
    city = fields.Char(
        string='City'
    )
    state_id = fields.Many2one(
        'res.country.state', readonly=False, store='True'
    )
    country_id = fields.Many2one(
        'res.country', readonly=False, store='True'
    )

    payment_ids = fields.One2many('property.payment.records', 'property_id')

    state = fields.Selection([  # Status of Property
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('deal_received', 'Deal Received'),
        ('deal_confirmed', 'Deal Confirmed'),
        ('agreement_pending', 'Agreement Due'),
        ('contract_pending', 'Contract Due'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
        ('cancelled', 'Cancelled')
    ], default='draft')

    # property connects to property.offer
    offer_ids = fields.One2many(
        'property.offer',
        inverse_name='property_id',
        string="Offers",
        domain=[('state', 'not in', ('draft', 'cancelled'))]
    )

    square_fit = fields.Float('Square Fit')
    per_units = fields.Integer('Units')

    def add_property(self):
        """
            Method for Publish property
        """
        for rec in self:
            existing_property = self.search([
                ('name', '=', rec.name),
                ('owner_id', '=', rec.owner_id.id),
                ('property_type', '=', rec.property_type),
                ('id', '!=', rec.id)
            ], limit=1)

            if existing_property:
                raise ValidationError(
                    f"{rec.name} with Owner {rec.owner_id.name} is already exist for {rec.property_type}!!")

        if not self.name: raise ValidationError("Please Enter Property Name!")
        if not self.property_type: raise ValidationError("Please Enter Property Type!")
        if not self.owner_id: raise ValidationError("Please Enter Owner!")
        self.state = 'available'

    def accept_deal(self):
        """
            Method that accept and confirm the deal
            If only one offer accepted then offer confirmed without opening wizard,
            otherwise, open wizard then choose offer to accept and reject other offers
        """

        accepted_offers = self.offer_ids.filtered(lambda o: o.state == 'interested')

        if len(accepted_offers) == 1:
            accepted_offers.state = 'accepted'
            self.state = 'deal_confirmed'
            return

        return {
            'type': 'ir.actions.act_window',
            'name': 'Accept anyone offer',
            'res_model': 'reject.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_property_id': self.id,
                'default_message': "Order Category and Setting Category is matched"
            }
        }

    def action_create_sale_deal(self):
        """
            Method that create sale deal for sale contract
        """

        offer = self.env['property.offer'].search([
            ('property_id', '=', self.id),
            ('state', '=', 'accepted'),
        ])

        if offer:
            agreement = self.env['property.sale.deal'].create({
                'property_id': self.id,
                'buyer_id': offer.partner_id.id,
                'owner_id': self.owner_id.id,
                'price': offer.your_price,
                'currency_id': offer.currency_id.id,
                'street': self.street,
                'street2': self.street2,
                'zip': self.zip,
                'city': self.city,
                'state_id': self.state_id.id,
                'country_id': self.country_id.id,
            })

            self.state = 'agreement_pending'

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'property.sale.deal',
                'res_id': agreement.id,
                'view_mode': 'form',
                'target': 'current',
            }

    """ Smart Button to view Payment """

    payment_count = fields.Integer(string="Offers", compute="_compute_payment_count")

    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = self.env['property.payment.records'].search_count([
                ('property_id', '=', rec.id)
            ])

    def action_view_payments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'res_model': 'property.payment.records',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'target': 'current'
        }

    """ ------------------------------- """
    """ Smart Button to View All Offers """
    """ ------------------------------- """

    offer_count = fields.Integer(string="Offers", compute="_compute_offer_count")

    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = self.env['property.offer'].search_count([
                ('property_id', '=', rec.id),
                ('state', '=', 'interested')
            ])

    def action_view_all_offers(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'All Offers',
            'res_model': 'property.offer',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id), ('state', '!=', 'cancelled')],
            'target': 'current'
        }

    def action_view_sale_deal(self):
        """
            Method to view property sale deal
        """

        sale_agreement = self.env['property.sale.deal'].search([
            ('property_id', '=', self.id)
        ], limit=1)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Agreement',
            'view_mode': 'form',
            'res_model': 'property.sale.deal',
            'res_id': sale_agreement.id,
            'target': 'current'
        }

    def action_create_rent_deal(self):
        """
            Method that create property Rent Contract
        """

        self.state = 'contract_pending'

        offer = self.env['property.offer'].search([
            ('property_id', '=', self.id),
            ('state', '=', 'accepted'),
        ])

        if offer:
            contract = self.env['property.rent.deal'].create({
                'property_id': self.id,
                'owner_id': self.owner_id.id,
                'tenant_id': offer.partner_id.id,
                'rent_amount': offer.your_price,
            })

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'property.rent.deal',
                'res_id': contract.id,
                'view_mode': 'form',
                'target': 'current',
            }

    def action_view_rent_deal(self):
        """
            Method to view property Rent Contract
        """

        rent_agreement = self.env['property.rent.deal'].search([
            ('property_id', '=', self.id)
        ], limit=1)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Rent Agreement',
            'view_mode': 'form',
            'res_model': 'property.rent.deal',
            'res_id': rent_agreement.id,
        }

    def action_cancel(self):
        """
            Method to cancel Property
        """

        if not self.offer_ids:
            raise ValidationError("No offers available")

        self.offer_ids.state = 'cancelled'
        self.state = 'cancelled'

    def action_reject_offer(self):
        """
            Method to reject all offers
        """

        return {
            'type': 'ir.actions.act_window',
            'name': 'Select Reason To Reject All Offers',
            'view_mode': 'form',
            'res_model': 'reject.reason.all.deal.line.wizard',
            'target': 'new',
            'context': {
                'default_property_id': self.id,
                'default_offer_id': self.offer_ids,
            }
        }

    def state_to_draft_server_action(self):
        for rec in self:
            rec.write({'state': 'draft'})
