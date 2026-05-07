from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime


class FeeStructure(models.Model):
    _name = 'fee.structure'
    _description = 'Fee Structure'
    _rec_name = 'name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Fee Structure Name', required=True)

    # Which class does this fee structure apply to
    standard_id = fields.Many2one('standard', string='Standard', required=True)

    # Fee line items (tuition, transport, library, etc.)
    fee_line_ids = fields.One2many('fee.structure.line', 'fee_structure_id', string='Fee Lines')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
    ], default='draft')

    # Total computed from lines
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total', currency_field='currency_id',
                                   store=True)

    academic_year = fields.Char(string="Academic Year", default=lambda self: self._get_academic_year())

    create_date = fields.Date('Create Date', default=fields.Date.today)
    last_date = fields.Date('Last Date')

    def _get_academic_year(self):
        year = datetime.now().year
        next_year = str(year + 1)[-2:]
        return f"{year}-{next_year}"

    @api.depends('fee_line_ids.amount')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(rec.fee_line_ids.mapped('amount'))

    def confirm_fee_structure(self):

        for rec in self:

            if not rec.fee_line_ids:
                raise ValidationError("Fee Structure must have at least one fee line")

            rec.write({
                'state': 'confirmed'
            })

    def return_to_draft(self):
        for rec in self:
            rec.write({
                'state': 'draft'
            })