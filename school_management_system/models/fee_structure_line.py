from odoo import fields, models, api
from odoo.exceptions import ValidationError

class FeeStructureLine(models.Model):

    _name = 'fee.structure.line'
    _description = 'Fee Structure Line'
    _rec_name = 'description'

    fee_structure_id = fields.Many2one('fee.structure', string='Fee Structure', ondelete='cascade')

    fee_type = fields.Selection([
        ('tuition', 'Tuition Fee'),
        ('transport', 'Transport Fee'),
        ('library', 'Library Fee'),
        ('sports', 'Sports Fee'),
        ('exam', 'Exam Fee'),
        ('other', 'Other')
    ], string='Fee Type', required=True)

    description = fields.Char(string='Description')
    currency_id = fields.Many2one('res.currency',  default=lambda self: self.env.company.currency_id.id)
    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id')