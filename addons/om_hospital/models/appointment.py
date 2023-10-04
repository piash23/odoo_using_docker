from odoo import _, api, fields, models


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Appointment Record"
    _rec_name = "patient_id"

    patient_id = fields.Many2one(
        comodel_name='hospital.patient', string='Patient', required=True)
    patient_gender = fields.Selection(related='patient_id.gender', readonly=False,
                                      help="non readonly can effect parent model")  # non readonly can effect parent model
    appointment_time = fields.Datetime(
        string='Appointment Time', required=True, default=fields.Datetime.now)
    booking_date = fields.Date(
        string='Booking Date', required=True, default=fields.Date.today)
    ref = fields.Char(string='Reference', required=False)
    

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        self.ref = self.patient_id.ref
