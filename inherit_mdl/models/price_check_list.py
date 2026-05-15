from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError


class PriceCheckList(models.Model):
    _name = 'price.checklist'
    _rec_name = 'checklist_name'

    checklist_name = fields.Char(string="Checklist Name")

    checklist_description = fields.Char(string="Description", help="This is the description of the checklist")

    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Priority")

    planned_date_begin = fields.Date("Planned Date Begin")

    planned_date_end = fields.Date("Planned Date End")
