from odoo import fields, models, api

class crmLead(models.Model):

    _inherit = 'crm.lead'

    sale_order_ids = fields.One2many('sale.order', 'crm_lead_id')

    sale_order_count = fields.Integer(string='Sale Order Count', compute='_compute_so_count')

    @api.depends('sale_order_ids')
    def _compute_so_count(self):
        for rec in self:
            rec.sale_order_count = len(rec.sale_order_ids)

    def action_view_sale_orders(self):

        return{
            'type': 'ir.actions.act_window',
            'name': 'Sale Orders',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('opportunity_id', '=', self.id)],
        }

    def _prepare_opportunity_quotation_context(self):
        res = super()._prepare_opportunity_quotation_context()

        res.update({
            'default_crm_lead_id': self.id
        })

        return res