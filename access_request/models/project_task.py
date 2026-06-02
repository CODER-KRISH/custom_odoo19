from odoo import fields, models, _


class ProjectTask(models.Model):
    """Extend task to show related access requests."""

    _inherit = "project.task"

    access_request_count = fields.Integer(
        string="Access Request Count",
        compute="_compute_access_request_count",
        help="Total number of access requests related to this task.",
    )

    def _compute_access_request_count(self):
        """Compute total access requests for task."""
        AccessRequest = self.env["odoo.sh.access.request"]

        for task in self:
            task.access_request_count = AccessRequest.search_count([
                ("task_id", "=", task.id)
            ])

    def action_open_access_requests(self):
        """Open access requests related to this task."""
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Access Requests"),
            "res_model": "odoo.sh.access.request",
            "view_mode": "list,form",
            "domain": [("task_id", "=", self.id)],
            "context": {
                "default_project_id": self.project_id.id,
                "default_task_id": self.id,
            },
        }