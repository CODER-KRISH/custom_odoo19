from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


class Project(models.Model):
    _inherit = "project.project"
    _order = "id desc"

    approver_ids = fields.Many2many(
        "res.users",
        "project_access_approver_rel",
        "project_id",
        "user_id",
        string="Access Approvers",
        help="Users who can approve or reject access requests for this project.",
    )

    access_request_count = fields.Integer(
        string="Access Request Count",
        compute="_compute_access_request_count",
        help="Total number of access requests for this project.",
    )

    access_register_count = fields.Integer(
        string="Access Register Count",
        compute="_compute_access_register_count",
        help="Total number of active/latest approved access records for this project.",
    )

    def _compute_access_request_count(self):
        """Compute total access requests for project."""
        AccessRequest = self.env["odoo.sh.access.request"]

        for project in self:
            project.access_request_count = AccessRequest.search_count([
                ("project_id", "=", project.id)
            ])

    def _compute_access_register_count(self):
        """Compute latest approved access register count for project."""
        AccessRequest = self.env["odoo.sh.access.request"]

        for project in self:
            register_ids = AccessRequest._get_access_register_ids(project.id)
            project.access_register_count = len(register_ids)

    def action_open_access_requests(self):
        """Open access requests related to this project."""
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Access Requests",
            "res_model": "odoo.sh.access.request",
            "view_mode": "list,form",
            "domain": [("project_id", "=", self.id)],
            "context": {
                "default_project_id": self.id,
            },
        }

    def action_open_access_register(self):
        """Open latest active approved access register for this project."""
        self.ensure_one()

        AccessRequest = self.env["odoo.sh.access.request"]
        register_ids = AccessRequest._get_access_register_ids(self.id)

        return {
            "type": "ir.actions.act_window",
            "name": "Access Register",
            "res_model": "odoo.sh.access.request",
            "view_mode": "list,form",
            "domain": [("id", "in", register_ids)],
            "context": {
                "default_project_id": self.id,
                "create": False,
            },
        }