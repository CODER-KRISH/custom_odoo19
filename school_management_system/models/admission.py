from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import ValidationError


class Admission(models.Model):
    _name = 'admission'
    _description = 'Admission'
    _rec_name = 'user_id'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    admission_sequence = fields.Char('Admission Sequence', default='New', store=True)
    user_id = fields.Many2one('res.users', string='Name', required=False)
    name = fields.Char(string='Student Name', required=False)
    enrollment_no = fields.Char(string='Enrollment Number')
    current_date = fields.Date(string='Date', default=fields.Date.today(), readonly=True)
    phone = fields.Char(string='Phone', related='user_id.phone', store=True)
    email = fields.Char(string='Email', related='user_id.email', store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])

    hobby_ids = fields.Many2many('hobby', 'admission_hobby_rel', 'admission_id', 'hobby_id', string='Hobby')
    student_id = fields.Many2one('student', string='Student')
    standard_id = fields.Many2one('standard', string='Standard')

    dob = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)

    @api.depends('dob')
    def _compute_age(self):
        """Compute Method to Calculate Age"""
        for rec in self:
            if rec.dob:
                rec.age = datetime.now().year - rec.dob.year

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('in_admission', 'In Admission'),
        ('terminate', 'Terminated'),
    ], default='draft', string='Status')

    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    zip = fields.Char(string='Zip')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string="State", readonly=False)
    country_id = fields.Many2one('res.country', string="Country", readonly=False)

    def search_student(self):
        return self.env['student'].search([('user_id', '=', self.user_id.id)], limit=1)

    def action_create_student_admission(self):
        """Method to create Student in student model"""
        for record in self:
            if not record.standard_id:
                raise ValidationError("Standard field cannot be empty")

            student = self.env['student']
            existing_admission = self.search([('user_id', '=', record.user_id.id), ('id', '!=', record.id)], limit=1)
            existing_student = student.search([('student_name', '=', record.user_id.name)], limit=1)

            if existing_admission or existing_student:
                raise ValidationError(f"Student with name {record.user_id.id} already exists")

            if record.admission_sequence == 'New':
                record.admission_sequence = self.env['ir.sequence'].next_by_code('admission')
                record.enrollment_no = self.env['ir.sequence'].next_by_code('enrollment')

            new_student = student.create({
                'state': 'admission_confirm',
                'user_id': record.user_id.id,
                'student_name': record.user_id.name,
                'dob': record.dob,
                'phone': record.phone,
                'email': record.email,
                'admission_id': record.id,
                'gender': record.gender,
                'standard_id': record.standard_id.id,
                'age': record.age,
                'hobby_ids': record.hobby_ids,
                'state_id': record.state_id.id,
                'street': record.street,
                'street2': record.street2,
                'zip': record.zip,
                'city': record.city,
                'country_id': record.country_id.id,
                'enrollment_no': record.enrollment_no
            })
            record.write({'state': 'approved'})
            record.user_id.write({'student_id': new_student.id})

    def confirm_student_admission(self):
        for rec in self:
            rec.write({'state': 'in_admission'})
            rec.search_student().write({'state': 'in_admission'})

    def update_student_admission(self):
        for rec in self:
            rec.write({'state': 'approved'})

    def terminate_student_admission(self):
        for rec in self:
            rec.write({'state': 'terminate'})
            rec.search_student().write({'state': 'terminate'})

    def write(self, vals):
        """ Write Method to Update Datas in Student model """
        res = super().write(vals)

        for record in self:
            student = self.search_student()

            if student:
                student.write({
                    'email': record.email,
                    'phone': record.phone,
                    'standard_id': record.standard_id.id,
                    'hobby_ids': record.hobby_ids,
                    'state_id': record.state_id.id,
                    'street': record.street,
                    'street2': record.street2,
                    'zip': record.zip,
                    'city': record.city,
                    'country_id': record.country_id.id,
                })

        return res

    def set_to_draft_server_action(self):
        for rec in self:
            rec.write({'state': 'draft'})
