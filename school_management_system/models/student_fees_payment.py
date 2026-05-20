from odoo import fields, models, api
from odoo.exceptions import ValidationError


class StudentFeesPayment(models.Model):
    _name = 'student.fees.payment'
    _description = 'Fee Payment'
    _rec_name = 'name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=False, default="New", copy=False, store=True)
    fees_id = fields.Many2one('student.fees', string='Fee Record', ondelete='cascade', tracking=True)
    student_id = fields.Many2one('student', related='fees_id.student_id', store=True, readonly=True, tracking=True)
    standard_id = fields.Many2one('standard', related='fees_id.standard_id', tracking=True)
    enrollment_no = fields.Char(string='Enrollment No', tracking=True)
    fee_name = fields.Char(string='Fee Type', related='fees_id.fee_structure_id.name', tracking=True)
    payment_date = fields.Datetime(string='Payment Date', required=False, tracking=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.ref("base.INR").id)
    amount = fields.Monetary(string='Amount Paid', required=True, currency_field='currency_id', tracking=True)
    notes = fields.Char(string='Remarks')
    payment_mode = fields.Selection([
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('online', 'Online Transfer'),
        ('card', 'Card'),
    ], string='Payment Mode', required=False, tracking=True)
    state = fields.Selection([
        ('fees_due', 'Fees Due'),
        ('paid', 'Paid')
    ], default='fees_due', tracking=True)
    fee_line_ids = fields.One2many(
        'fee.structure.line',
        related='fees_id.fee_line_ids',
        string='Fee Lines',
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """ Create Payment Invoice Number """
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('student.fees.payment')

        print("Generated Sequence:", self.env['ir.sequence'].next_by_code('student.fees.payment'))
        return super().create(vals_list)

    def pay_fees(self):
        for rec in self:
            if not rec.payment_mode:
                raise ValidationError("Payment mode cannot be empty!!")
            rec.write({
                'state': 'paid',
                'payment_date': fields.Datetime.now(),
            })
            rec.fees_id.write({'status': 'done'})