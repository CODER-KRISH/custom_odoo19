from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError

class PriceChecklistTemplate(models.Model):
    _name = 'price.checklist.template'

    name = fields.Char(required=True)

    checklist_ids = fields.Many2many('price.checklist')
