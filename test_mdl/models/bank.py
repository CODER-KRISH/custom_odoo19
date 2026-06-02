from odoo import fields, models, api

class Bank(models.Model):
    _name = 'bank'

    name = fields.Char(string="Bank Name")