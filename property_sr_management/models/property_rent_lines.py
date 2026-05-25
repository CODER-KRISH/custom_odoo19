from odoo import fields, models

from odoo_19.odoo.odoo.orm.decorators import ondelete


class PropertyRentLines(models.Model):
    _name = 'property.rent.lines'
    _description = 'Property Rent Lines'
    _order = 'due_date asc'
    _rec_name = 'property_id'

    contract_id = fields.Many2one(
        'property.rent.deal',
        required=True,
        ondelete='cascade',
    )

    property_id = fields.Many2one(
        'property',
        required=True,
        ondelete = 'cascade',
    )

    tenant_id = fields.Many2one(
        'res.users',
        required=True
    )

    due_date = fields.Date(required=True)

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )

    amount = fields.Monetary(
        currency_field='currency_id',
        required=True
    )

    status = fields.Selection([
        ('payment_due', 'Payment Due'),
        ('paid', 'Paid'),
    ], default='payment_due')

    payment_reference = fields.Char('Invoice No')

    payment_date = fields.Datetime(string='Payment Date')

    def action_mark_paid(self):

        """
            Method to pay rent line
        """

        today = fields.Datetime.now()

        for rec in self:
            if rec.status == 'paid':
                continue

            payment = self.env['property.payment.records'].create({
                'property_id': rec.property_id.id,
                'buyer_id': rec.tenant_id.id,
                'owner_id': rec.contract_id.owner_id.id,
                'property_type': rec.property_id.property_type,
                'offer_price': rec.amount,
                'payment_date': today,
            })

            rec.write({
                'payment_date': today,
                'payment_reference': payment.name,
                'status': 'paid'
            })

            total_rent_paid = sum(rec.contract_id.rent_line_ids.filtered(lambda l:l.status == 'paid').mapped('amount'))
            total_rent_amount = sum(rec.contract_id.rent_line_ids.mapped('amount'))

            if total_rent_paid == total_rent_amount:
                print('Condition true')
                self.contract_id.write({'state': 'done'})

    def cron_auto_pay_rent(self):
        today = fields.Datetime.now()

        rent_line = self.search([
            ('status', '=', 'payment_due')
        ], limit=1)

        if rent_line:
            payment = self.env['property.payment.records'].create({
                'property_id': rent_line.property_id.id,
                'buyer_id': rent_line.tenant_id.id,
                'owner_id': rent_line.contract_id.owner_id.id,
                'property_type': rent_line.property_id.property_type,
                'offer_price': rent_line.amount,
                'payment_date': today,
            })

            rent_line.payment_date = today
            rent_line.payment_reference = payment.name
            rent_line.status = 'paid'