from odoo import fields, models

class Subject(models.Model):
    _name = 'subject'
    _description = 'Subject'
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char('Name', required=True)

    standard_id = fields.Many2one('standard', string='Standard ID', required=True)

    subject_marks = fields.Float('Subject Marks')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active','Active'),
        ('removed','Removed'),
    ],default='draft')

    teacher_ids = fields.Many2many('teacher','subject_teacher_rel' , 'subject_id', 'teacher_id', string='Teachers')

    student_id = fields.Many2one(comodel_name='student',string='Student')
    teacher_id = fields.Many2one(comodel_name='teacher',string='Teacher')

    def confirm_subject(self):
        for rec in self:
            if rec.teacher_ids:
                # teachers = rec.teacher_ids.mapped('id')
                for teacher in rec.teacher_ids:
                    teacher.write({
                        'state': 'active'
                    })

            rec.write({
                'state': 'active',
            })

    def back_to_draft(self):
        self.write({'state': 'draft'})