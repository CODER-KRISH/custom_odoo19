from odoo import fields, models, api
from datetime import datetime

class Teacher(models.Model):
    _name = 'teacher'
    _description = 'Teacher'
    _rec_name = 'user_id'
    _order = 'id desc'

    user_id = fields.Many2one('res.users', string='Name', required=True)

    email = fields.Char(related='user_id.email', readonly=False)

    phone = fields.Char(related='user_id.phone', readonly=False)

    dob = fields.Date('Date of Birth')

    age = fields.Integer('Age', compute='_compute_age', store=True)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])

    current_date = fields.Date(string='Date', default=fields.Date.today(), readonly=True)

    type_address_label = fields.Char('Address')

    standard_id = fields.Many2one('standard', string='Standard')

    subject_ids = fields.Many2many('subject', 'subject_teacher_rel' , 'teacher_id', 'subject_id', string='Subject')

    street = fields.Char(string='street', readonly=False)

    street2 = fields.Char(string='street2', readonly=False)

    zip = fields.Char(string='zip', readonly=False)

    city = fields.Char(string='City', readonly=False)

    state_id = fields.Many2one('res.country.state', readonly=False)

    country_id = fields.Many2one('res.country', readonly=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminate', 'Terminated'),
    ], default='draft')

    # Compute Age Method
    @api.depends('dob')
    def _compute_age(self):
        for rec in self:
            if rec.dob:
                rec.age = datetime.now().year - rec.dob.year

    def confirm_teacher(self):
        for rec in self:
            rec.state = 'confirm'

    def return_draft(self):
        for rec in self:
            rec.state = 'draft'