import ast
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class saleOrder(models.Model):
    _inherit = 'sale.order'

    name_id = fields.Many2one('sale.order.info', string='Name')

    f_description = fields.Char(string='First Description')

    # category_ids = fields.One2many('res.config.settings', 'order_id')

    def action_change_state(self):
        for rec in self:

            if rec.state == 'draft':
                rec.write({'state': 'sale'})
            else:
                raise ValidationError("State Cannot be changed")

    def _prepare_invoice(self):
        res = super()._prepare_invoice()

        res['f_description'] = self.f_description

        return res

    # def action_confirm(self):
    #
    #     res = super().action_confirm()
    #
    #     for order in self:
    #         for picking in order.picking_ids:
    #
    #             picking.action_assign()
    #
    #             for move in picking.move_ids:
    #                 move.quantity = move.product_uom_qty
    #
    #             picking.button_validate()
    #
    #         all_invoices = order._create_invoices(order)
    #         all_invoices.action_post()
    #
    #     return res

    def action_confirm(self):

        print("Method Called")

        # param = self.env['ir.config_parameter'].sudo().get_param(
        #     'property_sale_and_rental_management_system.category_ids'
        # )
        #
        # allowed_category_ids = ast.literal_eval(param)
        # order_category_ids = self.order_line.product_template_id.categ_id.ids
        #
        # print("Allowed Categories:", allowed_category_ids, type(allowed_category_ids))
        # print("Order Line Categories:", order_category_ids, type(order_category_ids))
        # print("order_category_id in allowed_category_ids", order_category_ids in allowed_category_ids)
        #
        # # if not self.env.context.get('aryan') and any(order_category_id for order_category_id in order_category_ids) == any(setting_category_id for setting_category_id in allowed_category_ids):
        # if not self.env.context.get('aryan') and any(cat in allowed_category_ids for cat in order_category_ids):
        #     return{
        #         'type': 'ir.actions.act_window',
        #         'name': 'Confirmation',
        #         'res_model': 'sale.order.confirm.wizard',
        #         'view_mode': 'form',
        #         'target': 'new',
        #         'context': {
        #             'default_message': "Do you want to Proceed?" ,
        #             'so_id': self.id,
        #         }
        #     }

        return super().action_confirm()