from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError, UserError


class saleOrder(models.Model):
    _inherit = 'sale.order'

    template_ids = fields.Many2many('price.checklist.template', string="Template")
    all_checklists_ids = fields.One2many('checklist.template.line', 'sale_id')
    today = fields.Date(default=fields.Date.today)
    progress_point = fields.Float(string='Progress', default=0)
    state = fields.Selection(
        selection_add=[
            ('manager', 'Manager Approved'), ('boss', 'Boss Approved'), ('sale',)
        ]
    )

    origin_order_id = fields.Many2one('sale.order', string="Original Order")

    start_date = fields.Date(string='Start Date', copy=False)
    end_date = fields.Date(string='End Date', copy=False)

    html_timesheet = fields.Html(
        string='Timesheet',
        default=lambda self: self._get_empty_timesheet_table(),
        copy=False
    )

    @api.onchange('start_date', 'end_date')
    def _onchange_timesheet_dates(self):
        self.html_timesheet = self._get_empty_timesheet_table()

    def _get_empty_timesheet_table(self):
        start_date = self.start_date or ''
        end_date = self.end_date or ''

        return f"""
        <h3>Timesheet Records of Task</h3>
        <p>
            <b>Start Date:</b> <span>{start_date}</span>
            &nbsp;&nbsp;
            <b>End Date:</b> <span>{end_date}</span>
        </p>
        <table style="width:100%; border-collapse:collapse; font-size:13px;">
            <thead>
                <tr>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Task</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Parent Task</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Allocation Source</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Allocated Hours</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Source Allocated Hours</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Total Used Hours</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Total Used Last Month</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Used Hours Period</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Remaining Hours</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="9" style="text-align:center; padding:10px;">
                        No timesheet data available
                    </td>
                </tr>
            </tbody>
        </table>
        """

    def update_timesheet_server_action(self):

        for rec in self:
            task_rows = ""

            # example: get tasks from project linked with sale order
            tasks = self.env['project.task'].search([
                ('sale_order_id', '=', rec.id)
            ])

            if not tasks: raise ValidationError("Project/Tasks are not available for this Sale Order!")

            print("All Tasks with same sale Order...........",tasks)

            total_allocated = 0
            total_used = 0

            print("All time sheets...................",tasks.mapped('timesheet_ids'))

            for timesheet in tasks.mapped('timesheet_ids'):
                print("First Timesheet Name", timesheet.name)
                print("First Timesheet Name", timesheet.name)


            for task in tasks:

                print(task.child_ids)

                allocated_hours = task.allocated_hours or 0 # Particular Task Allocated Hours
                used_hours = task.effective_hours or 0 # Particular Task Used Hours
                remaining_hours = allocated_hours - used_hours # Particular Task Remaining Hours

                total_allocated += allocated_hours
                total_used += used_hours
                total_hours = allocated_hours + sum(task.child_ids.mapped('allocated_hours')) if task.child_ids else allocated_hours

                allocation_source = f"Inherited from {task.parent_id.name}" if task.parent_id else "Task itself"

                task_rows += f"""
                    <tr>
                        <td>{task.name or ''}</td>
                        <td style="text-align:center;">{task.parent_id.name or '-'}</td>
                        <td style="text-align:center;">{allocation_source}</td>
                        <td style="text-align:center;">{total_hours:.2f}</td>
                        <td style="text-align:center;">{allocated_hours:.2f}</td>
                        <td style="text-align:center;">{used_hours:.2f}</td>
                        <td style="text-align:center;">0.00</td>
                        <td style="text-align:center;">{used_hours:.2f}</td>
                        <td style="text-align:center;">{remaining_hours:.2f}</td>
                    </tr>
                """

                start_date = self.start_date or ''
                end_date = self.end_date or ''

                rec.html_timesheet = f"""
                <h3>Timesheet Usage by Task</h3>
                <p>
                <b>Start Date:</b> <span>{start_date}</span>
                &nbsp;&nbsp;
                <b>End Date:</b> <span>{end_date}</span>
                </p>
            

            <table style="width:100%; border-collapse:collapse; font-size:13px;">
                <thead>
                    <tr>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Task</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Parent Task</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Allocation Source</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Allocated Hours</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Source Allocated Hours</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Total Used Hours</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Total Used Last Month</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Used Hours Period</th>
                    <th style="background-color:#714b67; color:white; padding:2px 8px; text-align:left;">Remaining Hours</th>
                    </tr>
                </thead>

                <tbody>
                    {task_rows}
                    <tr style="font-weight:bold; border-top:1px solid #ddd;">
                        <td>Total</td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td style="text-align:center;">{total_allocated:.2f}</td>
                        <td style="text-align:center;">{total_used:.2f}</td>
                        <td style="text-align:center;">0.00</td>
                        <td style="text-align:center;">{total_used:.2f}</td>
                        <td style="text-align:center;">{total_allocated - total_used:.2f}</td>
                    </tr>
                </tbody>
            </table>
            """

    @api.onchange('template_ids')
    def _onchange_template_ids(self):

        self.all_checklists_ids = [(5, 0, 0)]
        self.progress_point = 0

        if self.template_ids:
            lines = []

            check_lists = self.template_ids.mapped('checklist_ids')

            for cl in check_lists:
                lines.append((0, 0, {
                    'checklist_name': cl.checklist_name,
                    'checklist_description': cl.checklist_description,
                    'today': self.today
                }))

            self.all_checklists_ids = lines

    @api.constrains('partner_id')
    def onchange_partner_id(self):
        delivery_adrs = self.partner_id.check_any_member_has_address()
        if delivery_adrs and delivery_adrs.type == 'delivery':
            self.partner_shipping_id = delivery_adrs.id
        else:
            self.partner_shipping_id = self.partner_id

    def find_config_currency(self):
        my_currency_id = self.env['ir.config_parameter'].sudo().get_param('inherit_mdl.my_currency_id')
        currency = self.env['res.currency'].browse(int(my_currency_id))
        return currency

    def check_min_limit(self):
        param = self.env['ir.config_parameter'].sudo()
        min_limit = float(param.get_param('inherit_mdl.min_limit'))

        print(self.find_config_currency().rate)
        print(min_limit * self.find_config_currency().rate)
        return min_limit * self.find_config_currency().rate

    def check_max_limit(self):
        param = self.env['ir.config_parameter'].sudo()
        max_limit = float(param.get_param('inherit_mdl.max_limit'))

        print(self.find_config_currency().rate)
        print(max_limit * self.find_config_currency().rate)
        return max_limit * self.find_config_currency().rate

    def state_to_boss(self):

        special_product = self.order_line.filtered(lambda line: line.is_special)

        if not special_product:
            self.write({'state': 'boss'})

        if special_product:
            all_approved = self.order_line.filtered(lambda line: line.is_approved)
            if not all_approved:
                raise ValidationError('Please Validate Special Product!')

    def state_to_manager(self):
        special_product = self.order_line.filtered(lambda line: line.is_special)
        if special_product:
            all_approved = self.order_line.filtered(lambda line: line.is_approved)
            if not all_approved:
                raise ValidationError('Please Validate Special Product!')

        if self.env.user.has_group('inherit_mdl.group_sale_manager') and not self.env.user.has_group(
                'inherit_mdl.group_sale_boss'):
            # Condition for Manager Login Only

            if self.amount_total * self.find_config_currency().rate >= self.check_max_limit():
                raise ValidationError(
                    f"""
                        Sale Amount : {self.amount_total} is greater than Max Amount: {self.check_max_limit()}
                        Boss Approval Required!
                    """
                )

            all_discount = self.order_line.filtered(lambda line: line.product_discount >= 50)
            if all_discount:
                raise ValidationError('Discount is above 50%, Boss Approval Required!')

            else:
                self.write({'state': 'manager'})

        if self.env.user.has_group('inherit_mdl.group_sale_boss'):
            # Condition for Boss Login
            self.state_to_boss()

    def action_confirm(self):

        for rec in self:

            # Special product validation
            special_product = rec.order_line.filtered(lambda l: l.is_special)
            if special_product:
                if rec.order_line.filtered(lambda l: not l.is_approved):
                    raise ValidationError('Please Validate Special Product!')

            currency = rec.find_config_currency()
            converted = rec.amount_total * currency.rate

            min_limit = rec.check_min_limit()
            max_limit = rec.check_max_limit()

            # Case 1: No limits configured
            if min_limit == 0 and max_limit == 0:
                continue

            # Case 2: Below min
            if converted < min_limit:
                continue

            # Case 3: Between min & max
            if min_limit < converted < max_limit:
                if rec.state not in ('manager', 'boss'):
                    raise ValidationError(
                        f"Sale Amount : {converted} is between Min Amount {min_limit} and Max Amount: {max_limit}\n Manager or Boss Approval Required!")

            # Case 4: Above max
            elif converted > max_limit:
                if rec.state != 'boss':
                    raise ValidationError(
                        f"Sale Amount: {converted} is greater than Max Amount: {max_limit}\nBoss Approval Required!")

        self.state = 'draft'
        return super().action_confirm()

    def action_open_split_wizard(self):
        """Action that split the sale order"""

        selected_lines = self.order_line.filtered(lambda l: l.tik_untick)

        if not selected_lines:
            raise UserError("Please select at least one line to split.")

        line_vals = []

        for line in selected_lines:
            line_vals.append((0, 0, {
                'product_id': line.product_id.id,
                'product_template_id': line.product_template_id.id,
                'qty': line.product_uom_qty,
            }))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Split Order',
            'res_model': 'split.order',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_order_line_ids': line_vals,
            }
        }

    def action_tick_untick(self):
        for line in self.order_line:
            line.tik_untick = not line.tik_untick

    split_order_count = fields.Integer(string="Splits", compute="_compute_split_so_count")

    def _compute_split_so_count(self):
        self.split_order_count = self.search_count([
            ('origin_order_id', '=', self.id)
        ])

    def action_view_split_orders(self):
        domain = [('origin_order_id', '=', self.id)]
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Split Orders',
            'res_model': 'sale.order',
            'view_mode': "list",
            'views': [(False, "list"), (False, "form")],
            'domain': domain,
        }

        split_so_ids = self.search(domain)
        if len(split_so_ids) == 1:
            action.update({
                "views": [(False, "form")],
                "res_id": split_so_ids.id
            })

        return action
