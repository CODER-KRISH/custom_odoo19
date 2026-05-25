from odoo import fields, models, api
from odoo.exceptions import ValidationError


class stockMove(models.Model):
    _inherit = 'stock.move'

    s_description = fields.Char(string="Second Description")

    f_description = fields.Char()

    def _get_new_picking_values(self):
        res = super()._get_new_picking_values()


        res.update({
            'f_description': self[0].f_description,
            'state': 'done'
        })

        return res

