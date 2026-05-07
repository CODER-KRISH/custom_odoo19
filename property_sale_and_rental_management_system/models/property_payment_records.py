from odoo import fields, models, api

class PropertyPaymentRecords(models.Model):
    _name = 'property.payment.records'
    _description = 'Property Payment Records'
    _rec_name = 'name'
    _order = 'id desc'

    """Payment Invoice Number as a name"""
    name = fields.Char(
        string="Invoice Number",
        required=False,
        copy=False,
        readonly=True,
        default='New'
    )

    """Property Name selection from model property"""
    property_id = fields.Many2one('property', string="Property", ondelete='cascade')

    """Property Buyer Name"""
    buyer_id = fields.Many2one('res.users', string="Buyer")

    """Property Owner Name"""
    owner_id = fields.Many2one('res.users', string="Owner")

    property_type = fields.Selection([
        ('sale', 'For Sale'),
        ('rent', 'For Rent')
    ])

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)

    offer_price = fields.Monetary(string="Price", currency_field='currency_id')

    payment_date = fields.Datetime(string="Payment Date")

    @api.model_create_multi
    def create(self, vals_list):
        """
            Method that create Payment Invoice Number
        """

        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('property.payment.records')
        return super().create(vals_list)