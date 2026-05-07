from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError

class projectTask(models.Model):

    _inherit = 'project.task'

    ticket_type = fields.Selection([
        ('installation', 'Installation'),
        ('repair', 'Repair'),
        ('amc', 'AMC')
    ], default='installation')

    product_id = fields.Many2one('product.product', string='Product')

    brand = fields.Char(string='Brand')

    serial_number = fields.Char(string='Serial Number')

    # bool field if type repair
    check_issue = fields.Boolean(default=False)

    def write(self, vals):
        res = super().write(vals)

        # Only proceed if stage_id is being changed
        if 'stage_id' in vals:
            for task in self:
                stage = task.stage_id

                if stage and stage.name.lower() == 'done':
                    self.ticket_to_solved(task)

        return res

    def ticket_to_solved(self, task):

        tickets = self.env['helpdesk.ticket'].search([
            ('fsm_task_ids', '=', task.id)
        ])

        if not tickets:
            return

        solved_stage = self.env['helpdesk.stage'].search([
            ('name', 'ilike', 'solved')
        ], limit=1)

        if solved_stage:
            tickets.write({'stage_id': solved_stage.id})