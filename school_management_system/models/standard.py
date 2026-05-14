from odoo import fields, models


class Standard(models.Model):
    _name = 'standard'
    _description = 'Standard'
    _rec_name = 'class_name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    class_name = fields.Char('Class Name', required=True)
    student_ids = fields.One2many('student', 'standard_id', string='Students')
    subject_ids = fields.One2many('subject', 'standard_id', string='Subjects')

    """ All Counts for Smart Buttons"""
    standard_teacher_count = fields.Integer(compute='_compute_standard_teacher_count')
    standard_student_count = fields.Integer(compute='_compute_students_count')
    standard_subjects_count = fields.Integer(compute='_compute_subjects_count')

    """ All Count Methods for Smart Buttons """
    def _compute_standard_teacher_count(self):
        for rec in self:
            rec.standard_teacher_count = self.env['teacher'].search_count([('standard_id', '=', rec.id)])

    def _compute_students_count(self):
        for rec in self:
            rec.standard_student_count = self.env['student'].search_count([('standard_id', '=', rec.id)])

    def _compute_subjects_count(self):
        for rec in self:
            rec.standard_subjects_count = self.env['subject'].search_count([('standard_id', '=', rec.id)])

    """ Required all Methods """
    def action_view_student(self):

        for rec in self:

            domain = [('standard_id', '=', rec.id)]
            if len(rec.student_ids) == 1:
                return rec.return_action(f'Class {rec.class_name} Students', 'student', 'form', domain)
            else:
                return rec.return_action(f'Class {rec.class_name} Students', 'student', 'list', domain)

    def action_view_subject(self):

        for rec in self:

            domain = [('standard_id', '=', rec.id)]
            if len(rec.subject_ids) == 1:
                return rec.return_action(f'Class {rec.class_name} Subjects', 'subject', 'form', domain)
            else:
                return rec.return_action(f'Class {rec.class_name} Subjects', 'subject', 'list', domain)

    def return_action(self, name, model, view_mode, domain):
        """ General Return method that works based on conditions """

        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': model,
            'view_mode': view_mode,
            'domain': domain,
        }