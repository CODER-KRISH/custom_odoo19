import random

from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError


class helpdesk_ticket(models.Model):
    _inherit = 'helpdesk.ticket'

    ticket_type = fields.Selection([
        ('installation', 'Installation'),
        ('repair', 'Repair'),
        ('amc', 'AMC')
    ], default='installation')

    product_id = fields.Many2one('product.product', string='Product')

    brand = fields.Char(string='Brand')

    serial_number = fields.Char(string='Serial Number')

    # Assign a technician as per the ticket type
    @api.onchange('ticket_type')
    def onchange_ticket_type(self):
        if self.ticket_type == 'installation':
            partners = self.env['res.users'].search([
                ('tech_type', '=', 'installation')
            ])

            if partners:
                partner = random.choice(partners)
                self.user_id = partner.id

        if self.ticket_type == 'repair':
            partners = self.env['res.users'].search([
                ('tech_type', '=', 'repair')
            ])

            if partners:
                partner = random.choice(partners)
                self.user_id = partner.id

        if self.ticket_type == 'amc':
            partners = self.env['res.users'].search([
                ('tech_type', '=', 'amc')
            ])

            if partners:
                partner = random.choice(partners)
                self.user_id = partner.id
