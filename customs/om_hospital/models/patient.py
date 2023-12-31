from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Patient Record'

    name = fields.Char(string='Name', required=True, tracking=True)
    date_of_birth = fields.Date(string='Date of Birth', tracking=True)
    age = fields.Integer(string='Age', tracking=True, compute='_compute_age', search='_search_age',
                         inverse='_inverse_compute_age')
    gender = fields.Selection([
        ("male", "Male"), ("female", "Female")])
    ref = fields.Char(string='Reference')
    active = fields.Boolean(string='Active', default=True)
    image = fields.Binary(string='Image')
    tag_ids = fields.Many2many('patient.tag', string='Tags')
    appointment_count = fields.Integer(string="Appointment Count", compute="_compute_appointment_count", store=True)
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string='Appointments')
    parent = fields.Char(string="Parent")
    marital_status = fields.Selection([('married', 'Married'), ('single', 'Single')], string="Marital Status",
                                      tracking=True)
    partner_name = fields.Char(string="Partner Name")
    is_birthday = fields.Boolean(string="Birthday", compute="_compute_is_birthday")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    website = fields.Char(string="Website")

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = self.env['hospital.appointment'].search_count([('patient_id', '=', rec.id)])

    @api.constrains('date_of_birth')
    def check_date_of_birth(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth > fields.date.today():
               raise ValidationError("Birthday is not acceptable")

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                rec.age = fields.Date.today().year - rec.date_of_birth.year
            else:
                rec.age = 0  # else is mendatory from odoo 14

    @api.onchange('age')
    def _inverse_compute_age(self):
        for rec in self:
            rec.date_of_birth = fields.Date.today() - relativedelta(years=rec.age)
    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code(
            'hospital.patient.sequence') or 'New'
        res = super(HospitalPatient, self).create(vals)
        return res

    def write(self, vals):
        if not self.ref:
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.patient.sequence') or 'New'
        res = super(HospitalPatient, self).write(vals)
        return res

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s - %s' % (rec.ref, rec.name)))
        return res

    @api.ondelete(at_uninstall=False)
    def check_appointment(self):
        for rec in self:
            if rec.appointment_ids:
                raise ValidationError(_("You cannot delete a patient with appointment"))

    def action_test(self):
        print("hello world")

    def _search_age(self, operator, value):
        date_of_birth = fields.date.today() - relativedelta(years=value)
        start_of_year = date_of_birth.replace(day=1, month=1)
        end_of_year = date_of_birth.replace(day=31, month=12)
        return [('date_of_birth', '>=', start_of_year), ('date_of_birth', '<=', end_of_year)]

    @api.depends('date_of_birth')
    def _compute_is_birthday(self):
        today = fields.date.today()
        for rec in self:
            if rec.date_of_birth.day == today.day and rec.date_of_birth.month == today.month:
                rec.is_birthday = True
            else:
                rec.is_birthday = False

    def action_view_appointment(self):
        return {
            'name': _('Appointments'),
            'res_model': 'hospital.appointment',
            'view_mode': 'list,form',
            'context': {'default_patient_id': self.id},
            'target': 'current',
            'domain': [('patient_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }
