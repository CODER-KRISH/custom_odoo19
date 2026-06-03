from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


class OdooSHAccessRequest(models.Model):
    _name = 'odoo.sh.access.request'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Odoo.sh Access Request"
    _order = "id desc"

    name = fields.Char(
        string="Reference",
        default="New",
        copy=False,
        tracking=True,
    )

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        tracking=True,
    )

    task_id = fields.Many2one(
        "project.task",
        string="Task",
        tracking=True,
    )

    user_id = fields.Many2one(
        "res.users",
        string="Requesting User",
        default=lambda self: self.env.user,
        tracking=True,
    )

    approver_ids = fields.Many2many(
        "res.users",
        string="Approvers",
        compute='_compute_project_id',
        store='True',
        tracking=True,
    )

    access_token = fields.Char(
        string="Access Token",
        copy=False,
        help="Unique access token for approval link or portal access.",
    )

    @api.depends('project_id')
    def _compute_project_id(self):
        for rec in self:
            if rec.project_id:
                rec.approver_ids = [(6, 0, rec.project_id.approver_ids.ids)]
            else:
                rec.approver_ids = [(5, 0, 0)]

    approved_by_id = fields.Many2one(
        "res.users",
        string="Approved By",
        tracking=True,
    )

    access_type = fields.Selection([
        ("git", "Git"),
        ("odoo_sh", "Odoo.sh"),
        ("git_odoo_sh", "Git & Odoo.sh"),
    ],
        string="Access Type",
        tracking=True,
    )

    environment = fields.Selection([
        ("staging", "Staging"),
        ("production", "Production"),
    ],
        string="Environment",
        tracking=True,
    )

    role = fields.Selection([
        ("tester", "Tester"),
        ("developer", "Developer"),
        ("admin", "Admin"),
    ],
        string="Role",
        tracking=True,
    )

    start_date = fields.Date(
        string="Start Date",
        tracking=True,
    )

    end_date = fields.Date(
        string="End Date",
        tracking=True,
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("revoked", "Revoked"),
    ],
        string="Status",
        default="draft",
        tracking=True,
    )

    github_username = fields.Char(
        string="GitHub Username",
        tracking=True,
        related='user_id.github_username'
    )

    rejection_reason = fields.Text(
        string="Reason",
        tracking=True,
        help="Reason entered by approver when request is rejected.",
    )

    approved_on = fields.Datetime(
        string="Approved On",
        tracking=True,
    )

    is_current_user_approver = fields.Boolean(
        compute="_compute_is_current_user_approver"
    )

    def _compute_is_current_user_approver(self):
        for rec in self:
            rec.is_current_user_approver = (self.env.user in rec.approver_ids or
                                            self.env.user.id == rec.project_id.user_id.id or
                                            self.env.user.has_group('access_request.group_ar_admin'))

    @api.model_create_multi
    def create(self, vals_list):
        """Create access request and assign sequence/access token."""
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "odoo.sh.access.request"
                ) or "New"

        return super().create(vals_list)

    @api.constrains("start_date", "end_date")
    def _validations(self):
        """Validate that end date is not earlier than start date."""
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date < record.start_date:
                    raise ValidationError("End Date cannot be earlier than Start Date.")

    def action_submit(self):
        """Submit draft request and send approval email."""
        for record in self:
            if record.state != "draft":
                raise UserError("Only draft requests can be submitted.")

            record.state = "submitted"
            record.action_send_mail()

    def action_send_mail(self):
        """Send approval email using mail template."""

        template = self.env.ref(
            "access_request.mail_template_access_request_approval",
            raise_if_not_found=False
        )

        for rec in self:
            approver_emails = ",".join(
                rec.approver_ids.mapped("email")
            )

            if template:
                template.send_mail(
                    rec.id,
                    force_send=True,
                    email_values={
                        "email_to": approver_emails,
                    }
                )

    def action_approve(self):
        """Approve submitted access request."""
        for record in self:
            if record.state != "submitted":
                raise UserError("Only submitted requests can be approved.")

            if (record.user_id == self.env.user and not
            self.env.user.has_group('access_request.group_ar_admin')):
                raise ValidationError("You cannot approve your own request.")

            if (self.env.user not in record.approver_ids and not
            self.env.user.has_group('access_request.group_ar_admin')):
                raise UserError("You are not a part of approvers.\nYou cannot approve the request!")

            if (
                    self.env.user == record.project_id.user_id or
                    self.env.user in record.approver_ids or
                    self.env.user.has_group('access_request.group_ar_admin')
            ):
                old_requests = self.search([
                    ("id", "!=", record.id),
                    ("project_id", "=", record.project_id.id),
                    ("user_id", "=", record.user_id.id),
                    ("state", "=", "approved"),
                ])

                old_requests.write({"state": "revoked"})

                record.write({
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_on": fields.Datetime.now(),
                    "rejection_reason": False,
                })

    def action_reject(self):
        """Open rejection wizard for submitted request."""
        self.ensure_one()

        if (
                self.env.user == self.project_id.user_id or
                self.env.user in self.approver_ids or
                self.env.user.has_group('access_request.group_ar_admin')
        ):

            if self.state != "submitted":
                raise UserError("Only submitted requests can be rejected.")

            return {
                "type": "ir.actions.act_window",
                "name": "Reject Access Request",
                "res_model": "access.request.reason",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "default_request_id": self.id,
                },
            }

    def action_revoke(self):
        """Revoke approved access request."""
        for record in self:
            if (
                    self.env.user == record.project_id.user_id or
                    self.env.user in record.approver_ids or
                    self.env.user.has_group('access_request.group_ar_admin')
            ):
                if record.state != "approved":
                    raise UserError("Only approved requests can be revoked.")

                record.state = "revoked"

    def action_set_to_draft(self):
        """Reset approved or rejected request to draft."""
        for record in self:
            if (
                    self.env.user == self.project_id.user_id or
                    self.env.user in self.approver_ids or
                    self.env.user.has_group('access_request.group_ar_admin')
            ):
                if record.state not in ["approved", "rejected", "submitted"]:
                    raise UserError("Only approved, submitted or rejected requests can be reset to draft.")

                record.write({
                    "state": "draft",
                })

    @api.model
    def _get_access_register_ids(self, project_id=False):
        """Return latest active approved request IDs per user and project."""

        approved_requests = self.env["odoo.sh.access.request"].search([
            ('state', '=', 'approved'),
            ("project_id", "=", project_id)
        ])

        return approved_requests

    def cron_create_revocation_reminders(self):
        """Create revocation reminder activities for expired approved requests."""
        today = fields.Date.today()

        expired_requests = self.search([
            ("state", "=", "approved"),
            ("end_date", "!=", False),
            ("end_date", "<=", today),
        ])

        activity_type = self.env.ref("mail.mail_activity_data_todo")

        for request in expired_requests:

            existing_activity = self.env["mail.activity"].search([
                ("res_model", "=", self._name),
                ("res_id", "=", request.id),
                ("activity_type_id", "=", activity_type.id),
                ("user_id", "=", request.approved_by_id.id),
            ], limit=1)

            if existing_activity:
                continue

            request.activity_schedule(
                activity_type_id=activity_type.id,
                user_id=request.approved_by_id.id,
                summary="Revoke expired access",
                note=f"Access request {request.name} has expired. Please revoke access.",
                date_deadline=today,
            )
