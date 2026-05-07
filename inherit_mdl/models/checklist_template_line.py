from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError

class CheckListTemplateLine(models.Model):
    _name = 'checklist.template.line'

    sale_id = fields.Many2one('sale.order', string="Sale Order")

    checklist_name = fields.Char(string='Checklist Name')

    checklist_description = fields.Char(string='Checklist Description')

    today = fields.Date(string='Date')


    def add_progress(self):

        line_ids = self.sale_id.template_ids.mapped('checklist_ids')

        if line_ids:
            self.sale_id.progress_point += 100 / len(line_ids)


    def remove_progress(self):

        line_ids = self.sale_id.template_ids.mapped('checklist_ids')

        if line_ids:
            self.sale_id.progress_point -= 100 / len(line_ids)