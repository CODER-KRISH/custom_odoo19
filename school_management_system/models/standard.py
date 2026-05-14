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


    """Smart Buttons for Students"""
    standard_student_count = fields.Integer(compute='_compute_students_count')

    def _compute_students_count(self):
        self.standard_student_count = self.env['student'].search_count([
            ('standard_id.class_name', '=', self.class_name)
        ])

    def action_view_student(self):
        domain = [('standard_id.class_name', '=', self.class_name)]

        action = {
            'type': 'ir.actions.act_window',
            'name': f'Class {self.class_name} Students',
            'res_model': 'student',
            'view_mode': "list",
            'views': [(False, "list"), (False, "form")],
            'domain': domain,
        }

        if len(self.student_ids) == 1:
            action.update({
                "views": [(False, "form")],
                "res_id": self.student_ids.id
            })

        return action

    """Smart Buttons for Subjects"""
    standard_subjects_count = fields.Integer(compute='_compute_subjects_count')

    def _compute_subjects_count(self):
        self.standard_subjects_count = self.env['subject'].search_count([
            ('standard_id.class_name', '=', self.class_name)
        ])

    def action_view_subject(self):
        domain = [('standard_id.class_name', '=', self.class_name)]

        action = {
            'type': 'ir.actions.act_window',
            'name': f'Class {self.class_name} Subjects',
            'res_model': 'subject',
            'view_mode': "list",
            'views': [(False, "list"), (False, "form")],
            'domain': domain,
        }

        if len(self.subject_ids) == 1:
            action.update({
                "views": [(False, "form")],
                "res_id": self.subject_ids.id
            })

        return action