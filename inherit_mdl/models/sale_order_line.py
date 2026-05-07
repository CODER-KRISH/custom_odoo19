from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError, UserError

class saleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_special = fields.Boolean(related='product_id.product_tmpl_id.special', store=True)
    is_approved = fields.Boolean(string="Approved", default=False, copy=False)
    bom_record_id = fields.Many2one('mrp.bom', string="Record Created")
    product_discount = fields.Float(string="Discount%")
    tik_untick = fields.Boolean(copy=False)

    def confirm_special_product(self):
        print("Done.........................")

        if self.env.user.has_group('inherit_mdl.group_sale_manager') and not self.env.user.has_group(
                'inherit_mdl.group_sale_boss'):
            print("Manager Logged In")
            if self.product_discount >= 50:
                raise UserError("Product Discount is above 50%, Boss approval required!")
            if self.product_discount < 50:
                self.is_approved = True

        elif self.env.user.has_group('inherit_mdl.group_sale_boss'):
            print("Boss Logged In")
            self.is_approved = True

        else: raise UserError("Manager or Boss Approval Required for Special Product Validation!")

    def create_copied_master_bom(self):

        product_bom = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', self.product_template_id.id),
        ])

        if not product_bom: raise ValidationError(f"BOM of {self.product_template_id.name} is not Found!")

        master = product_bom.filtered(lambda b: b.is_master)

        if not master: raise ValidationError(f"Master Bom of {self.product_template_id.name} is not Found!")

        if master:
            new_bom = master.copy()
            self.bom_record_id = new_bom.id

            bom_all_lines = new_bom.mapped('bom_line_ids')
            print(bom_all_lines)

            lines = self.fetch_all_components(new_bom,[])
            print(lines)

            bom_lines_vals = []
            for product in lines:
                bom_lines_vals.append((0, 0, {
                    'product_id': product.id
                }))

            new_bom.bom_line_ids = [(5, 0, 0)]
            new_bom.write({
                'bom_line_ids': bom_lines_vals
            })

            return new_bom

    def fetch_all_components(self, bom, all_components):

        if not bom.bom_line_ids:
            return all_components

        for line in bom.bom_line_ids:
            product = line.product_id

            if product not in all_components:
                all_components.append(product)

            child_bom = self.env['mrp.bom'].search([
                ('product_tmpl_id', '=', product.product_tmpl_id.id)
            ]).filtered(lambda b: b.is_master)

            if child_bom:
                self.fetch_all_components(child_bom, all_components)

        return all_components

    def view_copied_master_bom(self):

        if self.bom_record_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Confirm BOM',
                'res_model': 'mrp.bom',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.bom_record_id.id,
            }

        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Confirm BOM',
                'res_model': 'mrp.bom',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.create_copied_master_bom().id,
            }