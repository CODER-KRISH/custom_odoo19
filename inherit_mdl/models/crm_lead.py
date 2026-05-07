from odoo import models, fields, api
from datetime import timedelta
from odoo.fields import Date


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def cron_create_activity_based_on_last_date(self):
        leads = self.env['crm.lead'].search([
            ('stage_id.name', 'ilike', 'new')
        ])

        for lead in leads:
            now = fields.Date.today()

            last_msg = self.env['mail.message'].search([
                ('model', '=', lead._name),
                ('res_id', '=', lead.id)
            ], order='create_date desc', limit=1)

            last_act = self.env['mail.activity'].search([
                ('res_model', '=', lead._name),
                ('res_id', '=', lead.id),
            ], order='create_date desc', limit=1)

            last_msg_date = last_msg.date.date() if last_msg else False
            last_act_date = last_act.create_date.date() if last_act else False

            if lead.order_ids:
                last_so_date = max(lead.order_ids.mapped('date_order')).date()
            else: last_so_date = False

            last_meet_date = lead.meeting_display_date if lead.meeting_display_date else False

            print("Last Message Date.....................", last_msg_date)
            print("Last Mail Date.....................", last_act_date)
            print("Last Sale Order Date.....................", last_so_date)
            print("Last Meeting Date.....................", last_meet_date)

            condition_msg = last_msg_date and (now - last_msg_date) > timedelta(days=15)
            condition_act = last_act_date and (now - last_act_date) > timedelta(days=15)
            condition_meet = last_meet_date and (now - last_meet_date) > timedelta(days=15)
            condition_sod = last_so_date and (now - last_so_date) > timedelta(days=15)

            if condition_msg and condition_act and condition_meet and condition_sod:
                activity = self.env['mail.activity.type'].search([
                    ('name', '=', 'Email')
                ], limit=1)

                self.env['mail.activity'].create({
                    'res_model_id': self.env['ir.model']._get_id('crm.lead'),
                    'res_id': lead.id,
                    'user_id': lead.user_id.id or self.env.user.id,
                    'summary': 'Follow-up',
                    'note': 'No activity from last 15 days.',
                    'date_deadline': fields.Date.today(),
                    'activity_type_id': activity.id,
                })