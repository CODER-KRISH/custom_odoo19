import ast
from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    my_currency_id = fields.Many2one('res.currency')
    min_limit = fields.Monetary(string="Min Limit", currency_field='my_currency_id')
    max_limit = fields.Monetary(string="Max Limit", currency_field='my_currency_id')

    def set_values(self):
        super().set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('inherit_mdl.min_limit', str(self.min_limit) or 0.0)
        params.set_param('inherit_mdl.max_limit', str(self.max_limit) or 0.0)
        params.set_param('inherit_mdl.my_currency_id', self.my_currency_id.id or self.env.company.currency_id.id)

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()

        min_limit = params.get_param('inherit_mdl.min_limit', default='0.0')
        max_limit = params.get_param('inherit_mdl.max_limit', default='0.0')
        currency_id = params.get_param('inherit_mdl.my_currency_id')

        res.update({
            'min_limit': float(min_limit) if min_limit else 0.0,
            'max_limit': float(max_limit) if max_limit else 0.0,
            'my_currency_id': int(currency_id) if currency_id else self.env.company.currency_id.id,
        })

        return res
