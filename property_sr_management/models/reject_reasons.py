from odoo import fields, models, api

class RejectReasons(models.Model):
    _name = 'reject.reasons'
    _description = 'Reject Reasons'
    _rec_name = 'name'

    name = fields.Char(string='Reject Reason')