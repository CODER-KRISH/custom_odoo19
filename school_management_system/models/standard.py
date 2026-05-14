from odoo import fields, models


class Standard(models.Model):
    _name = 'standard'
    _description = 'Standard'
    _rec_name = 'class_name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Standard Name
    class_name = fields.Char('Class Name', required=True)

    # Connects to Students
    # relation needed to add multiple students in one standard
    student_ids = fields.One2many('student', 'standard_id', string='Students')

    # Connects to Subjects
    # relation needed to add multiple subjects in one standard
    subject_ids = fields.One2many('subject', 'standard_id', string='Subjects')

    def return_action(self, name, model, view_mode, domain):
        """ General Return method that works based on conditions """

        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': model,
            'view_mode': view_mode,
            'domain': domain,
        }

    standard_teacher_count = fields.Integer(compute='_compute_standard_teacher_count')

    def _compute_standard_teacher_count(self):
        for rec in self:
            rec.standard_teacher_count = self.env['teacher'].search_count([('standard_id', '=', rec.id)])

    """Smart Buttons for Students"""
    standard_student_count = fields.Integer(compute='_compute_students_count')

    def _compute_students_count(self):

        for rec in self:
            rec.standard_student_count = self.env['student'].search_count([('standard_id', '=', rec.id)])

    def action_view_student(self):

        for rec in self:

            domain = [('standard_id', '=', rec.id)]

            if len(rec.student_ids) == 1:
               return rec.return_action(f'Class {rec.class_name} Students', 'student', 'form', domain)

            else:
                return rec.return_action(f'Class {rec.class_name} Students', 'student', 'list', domain)

    """Smart Buttons for Subjects"""
    standard_subjects_count = fields.Integer(compute='_compute_subjects_count')

    def _compute_subjects_count(self):
        for rec in self:
            rec.standard_subjects_count = self.env['subject'].search_count([('standard_id', '=', rec.id)])

    def action_view_subject(self):

        for rec in self:

            domain = [('standard_id', '=', rec.id)]

            if len(rec.subject_ids) == 1:
                return rec.return_action(f'Class {rec.class_name} Subjects', 'subject', 'form', domain)

            else:
                return rec.return_action(f'Class {rec.class_name} Subjects', 'subject', 'list', domain)
