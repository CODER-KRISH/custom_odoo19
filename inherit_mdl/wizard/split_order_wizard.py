from odoo import api, models, fields
from odoo.exceptions import AccessError, ValidationError, UserError


class SplitOrderLines(models.TransientModel):
    _name = 'split.order.lines'

    split_order_id = fields.Many2one('split.order')
    product_id = fields.Many2one('product.product', string='Product')
    product_template_id = fields.Many2one('product.template', string='Product')
    qty = fields.Float(string='Quantity', default=0.00)


class SplitOrder(models.TransientModel):
    _name = 'split.order'

    order_line_ids = fields.One2many('split.order.lines', 'split_order_id')
    sale_order_id = fields.Many2one('sale.order')

    def action_split_order(self):
        print("Hello!")

        selected_lines = self.sale_order_id.order_line.filtered(lambda l: l.tik_untick)

        lines_invoiced = selected_lines.filtered(lambda line: line.qty_invoiced > 0)
        lines_delivered = selected_lines.filtered(lambda line: line.qty_delivered > 0)


        if lines_delivered and not lines_invoiced:
            picking = selected_lines.move_ids.mapped('picking_id').filtered(
                lambda p: p.picking_type_code == 'outgoing'
            )

            return_vals = []
            for line in picking.move_ids:
                return_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': 0.00
                }))
            return_picking = self.env['stock.return.picking'].create({
                'product_return_moves': return_vals,
            })
            if picking:
                return_picking.picking_id = picking[0]

            print(return_picking)

            for line in return_picking.product_return_moves:

                matched = self.order_line_ids.filtered(lambda l: l.product_id.id == line.product_id.id)

                if matched:
                    line.quantity = matched.qty
                else:
                    line.quantity = 0

            new_picking = return_picking._create_return()

            new_picking.action_confirm()
            new_picking.action_assign()
            new_picking.button_validate()


        # if any(line.qty_invoiced > 0 for line in selected_lines):
        if lines_invoiced:
            print("Some quantity is invoiced")

            # picking = self.sale_order_id.picking_ids.filtered(lambda p: p.picking_type_code == 'outgoing' and p.state == 'done')

            # picking = self.sale_order_id.picking_ids.filtered(
            #     lambda p: p.picking_type_code == 'outgoing'
            #               and p.state == 'done' or 'assigned'
            #               and any(prd in p.move_ids.mapped('product_id') for prd in selected_lines.mapped('product_id'))
            # )
            # print(picking)
            # picking = selected_lines.move_ids.picking_id

            picking = selected_lines.move_ids.mapped('picking_id').filtered(
                lambda p: p.picking_type_code == 'outgoing'
            )
            print(picking)

            return_vals = []
            for line in picking.move_ids:
                return_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': 0.00
                }))
            return_picking = self.env['stock.return.picking'].create({
                'product_return_moves': return_vals,
            })
            if picking:
                return_picking.picking_id = picking[0]

            print(return_picking)

            for line in return_picking.product_return_moves:

                matched = self.order_line_ids.filtered(lambda l: l.product_id.id == line.product_id.id)

                if matched:
                    line.quantity = matched.qty
                else:
                    line.quantity = 0

            new_picking = return_picking._create_return()

            # print(result)
            # new_picking = self.env['stock.picking'].browse(result.get('res_id'))

            new_picking.action_confirm()
            new_picking.action_assign()
            new_picking.button_validate()

            invoice = self.sale_order_id.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice')

            if invoice:
                reversal = self.env['account.move.reversal'].create({
                    'move_ids': [(6, 0, [invoice.id])],
                    'reason': 'Return of goods',
                    'journal_id': invoice.journal_id.id,
                })

                result = reversal.reverse_moves()

                credit_note = self.env['account.move'].browse(result.get('res_id'))

                qty_map = {
                    line.product_id.id: line.qty
                    for line in self.order_line_ids
                }

                for line in credit_note.invoice_line_ids:

                    if line.product_id.id in qty_map:
                        line.quantity = qty_map[line.product_id.id]
                    else:
                        line.unlink()

                credit_note.action_post()

        new_order = self.env['sale.order'].create({
            'partner_id': self.sale_order_id.partner_id.id,
            'origin': self.sale_order_id.name,
            'company_id': self.sale_order_id.company_id.id,
            'origin_order_id': self.sale_order_id.id,
        })

        for line in self.order_line_ids:
            so_line = selected_lines.filtered(lambda l: l.product_template_id.id == line.product_template_id.id)

            if so_line.product_uom_qty < line.qty: raise UserError(
                "Split quantity cannot be greater than main quantity")

            if line.qty == 0: raise UserError("Split quantity cannot be 0")

            self.env['sale.order.line'].create({
                'order_id': new_order.id,
                'product_id': line.product_id.id,
                'product_template_id': line.product_template_id.id,
                'name': line.product_template_id.id,
                'product_uom_qty': line.qty,
                'price_unit': line.product_template_id.list_price,
            })

            so_line.product_uom_qty -= line.qty

        for line in selected_lines:
            line.tik_untick = False