import warnings
from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


class PropertyOffer(models.Model):
    _name = 'property.offer'
    _description = 'Property Offer'
    _rec_name = 'partner_id'
    _order = 'id desc'

    property_id = fields.Many2one(
        'property',
        string="Property",
        required=True,
        ondelete="cascade"
    )

    property_type = fields.Selection([
        ('sale', 'For Sale'),
        ('rent', 'For Rent')
    ], string="Property Type", readonly=False)

    owner_id = fields.Many2one(
        'res.users',
        related='property_id.owner_id',
    )

    original_owner_id = fields.Many2one(
        'res.users',
        string="Owner"
    )

    buyer_id = fields.Many2one(
        'res.users',
        string="Buyer",
        required=False
    )

    tenant_id = fields.Many2one(
        'res.users',
        string="Tenant",
        required=False,
    )

    """
        Compute Method for label of Buyer/Tenant
        if sale then label is Buyer
        if Rent then label is Tenant
    """

    partner_id = fields.Many2one('res.users', compute="_compute_party", store=True)

    @api.depends('property_type', 'buyer_id', 'tenant_id')
    def _compute_party(self):
        for rec in self:
            if rec.property_type == 'sale':
                rec.partner_id = rec.buyer_id.id
            if rec.property_type == 'rent':
                rec.partner_id = rec.tenant_id.id

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )

    price = fields.Monetary(
        related='property_id.amount',
        string="Amount",
        currency_field='currency_id',
        required=True
    )

    your_price = fields.Monetary(
        string="Your Price",
        currency_field='currency_id',
        required=True
    )

    offer_date = fields.Date(
        string="Offer Date",
        default=fields.Date.today
    )

    reject_reason = fields.Char(
        string="Rejection Reason",
        readonly=True
    )

    street = fields.Char(
        string='Street',
        related='property_id.street',
        readonly=False
    )
    street2 = fields.Char(
        string='Street 2',
        related='property_id.street2',
        readonly=False
    )
    zip = fields.Char(
        string='Zip',
        related='property_id.zip',
        readonly=False
    )

    city = fields.Char(
        string='City',
        related='property_id.city',
        readonly=False
    )
    state_id = fields.Many2one(
        'res.country.state',
        related='property_id.state_id',
        readonly=False
    )
    country_id = fields.Many2one(
        'res.country',
        related='property_id.country_id',
        readonly=False
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('interested', 'Interested'),
        ('accepted', 'Accepted'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], default='draft', string="Status")

    def action_accept_offer(self):
        """
            Method that make an offer for particular property
        """

        """ Needed for if property sold then Owner has to be changed """
        self.original_owner_id = self.owner_id.id

        """ Check if not your_price then raise ValidationError """
        if not self.your_price: raise ValidationError("Customer Price cannot be empty")

        """ Raise ValidationError if Seller and Buyer are Same """
        if self.owner_id.id == self.buyer_id.id or self.owner_id.id == self.tenant_id.id:
            raise ValidationError("Owner and Seller cannot be same!!")

        """ Search in self to found existing offer is found with same customer with same property """
        existing_offer = self.search([
            ('property_id', '=', self.property_id.id),
            ('partner_id', '=', self.partner_id.id),
            ('id', '!=', self.id)
        ])

        """ If existing offer is found then raise ValidationError and self.offer state is cancelled """
        if existing_offer:
            self.reject_reason = "Your offer has been cancelled due to your existing offer is found!!"
            self.state = 'cancelled'

        existing_running_tenant = self.env['property.rent.deal'].search([
            ('tenant_id', '=', self.tenant_id.id),
            ('state', '=', 'running')
        ])

        if existing_running_tenant:
            self.reject_reason = "Your offer has been cancelled due to your rent contract is in running state!!"
            self.state = 'cancelled'

        else:
            self.property_id.state = 'deal_received'
            self.state = 'interested'

    def action_cancel_offer(self):
        """
            Method that cancel offer for particular property
        """

        for rec in self:
            offers = rec.property_id.offer_ids.filtered(lambda l: l.state == 'interested' or l.state == 'accepted')
            if len(offers) == 1: rec.property_id.write({'state': 'available'})
            rec.write({'state': 'cancelled', 'reject_reason': 'You cancelled your offer!!'})

    def property_offer_state_to_draft_server_action(self):
        for rec in self:
            rec.state = 'draft'
