from odoo import _, api, fields, models
import datetime
from odoo.exceptions import ValidationError


class CancelAppointmentWizard(models.TransientModel):
    _name = 'cancel.appointment.wizard'
    _description = 'Cancel Appointment Wizard'

    @api.model
    def default_get(self, fields):
        res = super(CancelAppointmentWizard, self).default_get(fields)
        # active_id = self.env.context.get('active_id')
        # if active_id:
        #     res.update({'appointment_id': active_id})
        res['cancellation_date'] = datetime.date.today()
        return res

    appointment_id = fields.Many2one(
        "hospital.appointment", string="Appointment", domain="[('state', '!=', 'done'), ('priority', '!=', '3')]"
    )
    cancel_reason = fields.Text(string="Reason", required=False)
    cancellation_date = fields.Date(string="Date", required=True)

    def action_cancel_appointment(self):
        if self.appointment_id.booking_date <= fields.date.today():
            raise ValidationError(_("Cancellation date should be greater than booking date"))

        self.appointment_id.write({'state': 'cancel'})
        print("Appointment Cancelled")
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
