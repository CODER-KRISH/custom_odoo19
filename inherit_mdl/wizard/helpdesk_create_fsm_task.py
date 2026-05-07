from odoo import models, fields, api


class HelpdeskCreateFsmTask(models.TransientModel):
    _inherit = 'helpdesk.create.fsm.task'

    def _generate_task_values(self):

        res = super()._generate_task_values()

        res.update({
            'serial_number': self.helpdesk_ticket_id.serial_number,
            'product_id': self.helpdesk_ticket_id.product_id.id,
            'brand': self.helpdesk_ticket_id.brand,
            'ticket_type': self.helpdesk_ticket_id.ticket_type,
            'user_ids': [(6, 0, [self.helpdesk_ticket_id.user_id.id])] if self.helpdesk_ticket_id else False
        })

        return res