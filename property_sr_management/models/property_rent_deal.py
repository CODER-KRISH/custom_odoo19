from odoo import fields, models, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class PropertyRentDeal(models.Model):
    _name = 'property.rent.deal'
    _description = 'Property Rent Deals'
    _rec_name = 'property_id'
    _order = 'id desc'

    property_id = fields.Many2one(
        'property',
        string='Property',
        required=True,
        ondelete='cascade'
    )

    owner_id = fields.Many2one(
        'res.users',
        string='Owner',
        required=True
    )

    tenant_id = fields.Many2one(
        'res.users',
        string='Tenant',
        required=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )

    rent_amount = fields.Monetary(
        string='Monthly Rent',
        currency_field='currency_id',
        required=True
    )

    start_date = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.today
    )

    end_date = fields.Date(
        string='End Date',
        required=False
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Done'),
    ], default='draft')

    rent_line_ids = fields.One2many(
        'property.rent.lines',
        'contract_id',
        string='Rent History',
        ondelete='cascade'
    )

    total_rent_amount = fields.Monetary(
        string='Total Rent Amount',
        currency_field='currency_id',
        compute='_compute_rent_payment',
        store=True 
    )

    paid_amount = fields.Monetary(
        string='Paid Amount',
        currency_field='currency_id',
        compute='_compute_rent_payment',
        store=True
    )

    remaining_rent_amount = fields.Monetary(
        string='Remaining Amount',
        currency_field='currency_id',
        compute='_compute_rent_payment',
        store=True
    )

    """ Method that calculates paid rent and remaining rent amount """
    @api.depends('rent_line_ids', 'rent_line_ids.amount', 'rent_line_ids.status')
    def _compute_rent_payment(self):
        for rec in self:

            total_rent = sum(rec.rent_line_ids.mapped('amount'))
            total_paid = sum(rec.rent_line_ids.filtered(lambda l: l.status == 'paid').mapped('amount'))

            rec.total_rent_amount = total_rent
            rec.paid_amount = total_paid
            rec.remaining_rent_amount = total_rent - total_paid

    def action_confirm(self):

        """
            Method that confirm the rent agreement and
            call method generate_monthly_rent()
            to generate monthly rent lines.
        """

        if not self.end_date:
            raise ValidationError("Please enter a valid end date")

        for rec in self:
            if rec.end_date <= rec.start_date:
                raise ValidationError("End Date must be greater than Start Date!")

            rec.state = 'running'
            rec.property_id.state = 'rented'
            rec.generate_monthly_rent()

        offer = self.env['property.offer'].search([
            ('property_id', '=', self.property_id.id),
            ('state', '=', 'accepted'),
        ])

        if offer:
            offer.state = 'closed'

    def generate_monthly_rent(self):

        """
            Method that generates rent lines from contract strat date to end date
        """

        for rec in self:
            current_date = rec.start_date

            while current_date <= rec.end_date:

                existing = self.env['property.rent.lines'].search([
                    ('contract_id', '=', rec.id),
                    ('due_date', '=', current_date)
                ], limit=1)

                if not existing:
                    self.env['property.rent.lines'].create({
                        'contract_id': rec.id,
                        'property_id': rec.property_id.id,
                        'tenant_id': rec.tenant_id.id,
                        'due_date': current_date,
                        'amount': rec.rent_amount,
                    })

                current_date += relativedelta(months=1)