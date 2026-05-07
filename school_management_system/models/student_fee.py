from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import ValidationError


class StudentFees(models.Model):
    """
    Actual fee record assigned per student per term.
    Created when a student is admitted or at start of term.
    """
    _name = 'student.fees'
    _description = 'Student Fees'
    _rec_name = 'student_id'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Fee Reference', default='New', copy=False)

    # Core relations
    student_id = fields.Many2one('student', string='Student', required=True, ondelete='cascade')
    standard_id = fields.Many2one(
        'standard', string='Standard',
        related='student_id.standard_id', store=True, readonly=True
    )
    enrollment_no = fields.Char(related='student_id.enrollment_no', string='Enrollment No')

    fee_structure_id = fields.Many2one('fee.structure', string='Fee Structure', ondelete='cascade')

    # Term / billing period
    term = fields.Selection([
        ('term1', 'Term 1'),
        ('term2', 'Term 2'),
        ('term3', 'Term 3'),
        ('annual', 'Annual'),
    ], string='Term', required=False)

    academic_year = fields.Char(
        string='Academic Year',
        default=lambda self: self.env['fee.structure']._get_academic_year()
    )

    due_date = fields.Date(string='Due Date', required=True, related='fee_structure_id.last_date')
    issue_date = fields.Date(string='Payment Date', default=fields.Date.today)

    # Amounts
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    total_amount = fields.Monetary(string='Total Amount', related='fee_structure_id.total_amount', store=True,
                                   currency_field='currency_id')
    discount = fields.Monetary(string='Discount')
    net_amount = fields.Monetary(string='Net Amount', compute='_compute_net', store=True)
    paid_amount = fields.Monetary(string='Paid Amount', compute='_compute_paid', store=True)
    balance = fields.Monetary(string='Balance Due', compute='_compute_balance', store=True)

    # Payment lines
    payment_ids = fields.One2many('student.fees.payment', 'fees_id', string='Payments')

    # Fee types
    fee_line_ids = fields.One2many(
        'fee.structure.line',
        related='fee_structure_id.fee_line_ids',
        string='Fee Lines',
        readonly=True,
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='Status')

    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft')

    @api.depends('total_amount', 'discount')
    def _compute_net(self):
        for rec in self:
            rec.net_amount = rec.total_amount - rec.discount

    @api.depends('payment_ids.amount')
    def _compute_paid(self):
        for rec in self:
            rec.paid_amount = sum(rec.payment_ids.mapped('amount'))

    @api.depends('net_amount', 'paid_amount')
    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.net_amount - rec.paid_amount


    @api.onchange('fee_structure_id')
    def _onchange_fee_structure(self):
        """Auto-fill academic year from structure"""
        if self.fee_structure_id:
            self.academic_year = self.fee_structure_id.academic_year


    def action_confirm(self):
        for rec in self:

            paid_fees = self.search([
                ('fee_structure_id', '=', rec.fee_structure_id.id),
                ('student_id', '=', rec.student_id.id),
                ('id', '!=', rec.id)
            ])

            if paid_fees: raise ValidationError("Fees already paid!")

            rec.status = 'confirmed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.state in ('confirmed', 'partial', 'overdue'):
                if rec.balance <= 0:
                    rec.state = 'paid'
                elif 0 < rec.paid_amount < rec.net_amount:
                    rec.state = 'partial'
        return res


    def confirm_and_next(self):

        for rec in self:

            invoice = self.env['student.fees.payment'].create({
                'fees_id': rec.id,
                'student_id': rec.student_id.id,
                'standard_id': rec.standard_id.id,
                'enrollment_no': rec.enrollment_no,
                'fee_line_ids': rec.fee_line_ids.mapped('id'),
                'payment_date': rec.issue_date,
                'amount': rec.total_amount
            })

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'student.fees.payment',
                'res_id': invoice.id,
                'view_mode': 'form',
                'target': 'current',
            }

    def back_to_draft(self):
        for rec in self:
            rec.write({
                'status': 'draft'
            })