from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime


class Announcement(models.Model):
    _name = 'announcement'
    _description = 'School Announcement'
    _rec_name = 'title'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Announcement Reference',
        default='New',
        copy=False,
        readonly=True,
        tracking=True,
    )

    title = fields.Char(string='Title', tracking=True)

    announcement_type = fields.Selection([
        ('general', 'General'),
        ('exam', 'Exam'),
        ('fee', 'Fee'),
        ('event', 'Event'),
        ('holiday', 'Holiday'),
    ], string='Type', default='general', tracking=True)

    # Audience targeting
    audience = fields.Selection([
        ('all', 'All'),
        ('students', 'Students Only'),
        ('teachers', 'Teachers Only'),
        ('parents', 'Parents Only'),
    ], string='Audience', default='all', tracking=True)


    academic_year = fields.Char(
        string='Academic Year',
        default=lambda self: self._get_academic_year(),
    )

    def _get_academic_year(self):
        year = datetime.now().year
        return f"{year}-{str(year + 1)[-2:]}"

    published_by = fields.Many2one(
        'res.users',
        string='Published By',
        default=lambda self: self.env.user,
    )

    publish_date = fields.Date(string='Publish Date', default=fields.Date.today)
    expiry_date = fields.Date(string='Expiry Date')

    description = fields.Html(string='Description', required=True)

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'announcement_attachment_rel',
        'announcement_id',
        'attachment_id',
        string='Attachments',
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='Status', tracking=True)

    # ── Constraints ────────────────────────────────────────────────────────────

    @api.constrains('publish_date', 'expiry_date')
    def _check_dates(self):
        for rec in self:
            if rec.publish_date and rec.expiry_date:
                if rec.expiry_date < rec.publish_date:
                    raise ValidationError('Expiry Date cannot be before Publish Date.')

    # ── Actions ────────────────────────────────────────────────────────────────

    def action_publish(self):
        for rec in self:
            if not rec.description:
                raise ValidationError('Please add a description before publishing.')
            if rec.name == 'New':
                rec.name = self.env['ir.sequence'].next_by_code('announcement') or 'New'
            rec.state = 'published'

    def action_expire(self):
        for rec in self:
            rec.state = 'expired'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'