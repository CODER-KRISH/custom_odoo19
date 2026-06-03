from odoo import fields, models, _
from odoo.exceptions import ValidationError, UserError


class AccessRequestReason(models.TransientModel):
    """Wizard to reject access request with mandatory reason."""

    _name = "access.request.reason"
    _description = "Access Request Rejection Reason"

    request_id = fields.Many2one(
        "odoo.sh.access.request",
        string="Access Request",
        required=True,
        help="Access request that will be rejected.",
    )

    reason = fields.Text(
        string="Rejection Reason",
        required=True,
        help="Reason for rejecting the access request.",
    )

    def action_confirm_rejection(self):
        """Reject access request and save rejection reason."""
        self.ensure_one()

        if not self.reason:
            raise ValidationError("Rejection reason is required.")

        if self.request_id.state != "submitted":
            raise UserError("Only submitted requests can be rejected.")

        self.request_id.write({
            "state": "rejected",
            "rejection_reason": self.reason,
        })