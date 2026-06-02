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
        tracking=True,
    )

    access_token = fields.Char(
        string="Access Token",
        copy=False,
        help="Unique access token for approval link or portal access.",
    )

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.approver_ids = [(6, 0, self.project_id.approver_ids)]
        else:
            self.approver_ids = [(5, 0, 0)]

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

    @api.model_create_multi
    def create(self, vals_list):
        """Create access request and assign sequence/access token."""
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "odoo.sh.access.request"
                ) or "New"

        return super().create(vals_list)

    def write(self, vals):
        """Update access request and sync GitHub username on user."""
        res = super().write(vals)

        if vals.get('github_username'):
            for record in self:
                if record.user_id and record.github_username:
                    record.user_id.github_username = record.github_username

        return res

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
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

        return True

    def action_approve(self):
        """Approve submitted access request."""
        for record in self:
            if record.state != "submitted":
                raise UserError("Only submitted requests can be approved.")

            if record.user_id == self.env.user:
                raise ValidationError("You cannot approve your own request.")

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

        return True

    def action_reject(self):
        """Open rejection wizard for submitted request."""
        self.ensure_one()

        if self.state != "submitted":
            raise UserError("Only submitted requests can be rejected.")

        if (
                self.env.user not in self.project_id.approver_ids
                and not self.env.user.has_group("project.group_project_manager")
        ):
            raise UserError("You are not allowed to reject this request.")

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
            if record.state != "approved":
                raise UserError("Only approved requests can be revoked.")

            record.state = "revoked"

        return True

    def action_set_to_draft(self):
        """Reset approved or rejected request to draft."""
        for record in self:
            if record.state not in ["approved", "rejected", "submitted"]:
                raise UserError("Only approved or rejected requests can be reset to draft.")

            record.write({
                "state": "draft",
            })

        return True

    @api.model
    def _get_access_register_ids(self, project_id=False):
        """Return latest active approved request IDs per user and project."""
        domain = [("state", "=", "approved")]

        if project_id:
            domain.append(("project_id", "=", project_id))

        approved_requests = self.search(domain, order="user_id, project_id, end_date desc, id desc")

        register_ids = []
        grouped_data = {}

        for request in approved_requests:
            key = (request.project_id.id, request.user_id.id)
            grouped_data.setdefault(key, []).append(request)

        for requests in grouped_data.values():
            no_end_date_request = requests.filtered(lambda r: not r.end_date)
            if no_end_date_request:
                register_ids.append(no_end_date_request[0].id)
            else:
                register_ids.append(requests[0].id)

        return register_ids

    @api.model
    def action_open_global_access_register(self):
        """Open global access register records."""
        register_ids = self._get_access_register_ids()

        return {
            "type": "ir.actions.act_window",
            "name": "Access Register",
            "res_model": "odoo.sh.access.request",
            "view_mode": "list,form",
            "domain": [("id", "in", register_ids)],
            "context": {"create": False},
        }

    @api.model
    def _cron_create_revocation_reminders(self):
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