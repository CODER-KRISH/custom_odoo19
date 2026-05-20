from odoo import fields, models, api

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
    student_id = fields.Many2one('student', string='Student', required=True, ondelete='cascade')
    standard_id = fields.Many2one('standard', string='Standard', related='student_id.standard_id', store=True, readonly=True)
    enrollment_no = fields.Char(related='student_id.enrollment_no', string='Enrollment No')
    fee_structure_id = fields.Many2one('fee.structure', string='Fee Structure', ondelete='cascade')
    academic_year = fields.Char(string='Academic Year', related='fee_structure_id.academic_year')
    due_date = fields.Date(string='Due Date', required=True, related='fee_structure_id.last_date')
    issue_date = fields.Date(string='Payment Date', default=fields.Date.today)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.ref("base.INR").id)
    total_amount = fields.Monetary(string='Total Amount', related='fee_structure_id.total_amount', store=True, currency_field='currency_id')
    payment_ids = fields.One2many('student.fees.payment', 'fees_id', string='Payments')
    fee_line_ids = fields.One2many(
        'fee.structure.line',
        related='fee_structure_id.fee_line_ids',
        string='Fee Lines',
        readonly=True,
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('fail', 'Failed')
    ], default='draft')

    def action_confirm(self):

        already_paid = self.search_count([
            ('fee_structure_id', '=', self.fee_structure_id.id),
            ('student_id', '=', self.student_id.id),
            ('id', '!=', self.id)
        ])

        self.status = 'fail' if already_paid else 'confirmed'

        if already_paid:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Payment Failed - Fees already paid!',
                    'type': 'danger',
                }
            }

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

    def search_invoice(self):
        return self.env['student.fees.payment'].search([('fees_id', '=', self.id)], limit=1)

    def view_invoice(self):
        invoice = self.search_invoice()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'student.fees.payment',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def print_invoice(self):
        invoice = self.search_invoice()

        return self.env.ref(
            'school_management_system.action_report_student_fee_receipt'
        ).report_action(invoice)
