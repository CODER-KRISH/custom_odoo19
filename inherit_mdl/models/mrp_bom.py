from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError

class mrp_bom(models.Model):
    _inherit = 'mrp.bom'

    is_master = fields.Boolean(default=False, string="Master", copy=False)

    def check_any_bom_is_master(self):

        all_bom = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', self.product_tmpl_id.id)
        ])

        all_bom -= self._origin

        any_is_master = all_bom.filtered(lambda bom: bom.is_master)

        if any_is_master: return any_is_master
        else: return False

    @api.onchange('is_master')
    def onchange_is_master(self):

        duplicate_master_found = self.check_any_bom_is_master()

        if duplicate_master_found:
            raise ValidationError("Master BOM can be One Only!")