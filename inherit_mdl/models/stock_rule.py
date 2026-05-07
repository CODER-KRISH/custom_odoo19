from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError

class stockRule(models.Model):

    _inherit = 'stock.rule'

    def _get_matching_bom(self, product_id, company_id, values):
        bom = super()._get_matching_bom(product_id, company_id, values)

        sale_line_id = values.get('sale_line_id')

        if sale_line_id:

            sale_line = self.env['sale.order.line'].browse(sale_line_id)

            if sale_line and sale_line.bom_record_id:
                return sale_line.bom_record_id

        return bom