from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError

class saleOrderInfo(models.Model):

    _name = 'sale.order.info'
    _rec_name = 'name'

    name = fields.Char(string="Name")