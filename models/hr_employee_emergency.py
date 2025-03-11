from odoo import models, fields, api

class HrEmployeeEmergency(models.Model):
    _name = 'hr.employee.emergency'
    _description = 'Employee Emergency Contact Details'
    _order = 'sequence, id'
    
    name = fields.Char(string="Name", required=True)
    # training_year = fields.Date(string="Year")
    telephone_no= fields.Text(string="Telephonr No")
    mobile_no = fields.Text(string="Mobile No")
    contact_address = fields.Text(string="Contact Address")
    # street = fields.Char(string="Street", help="Street address")
    # street2 = fields.Char(string="Street 2", help="Additional street address information")
    # city = fields.Char(string="City")
    # state_id = fields.Many2one('res.country.state', string="State")
    # zip = fields.Char(string="ZIP")
    # country_id = fields.Many2one('res.country', string="Country")
    # ADDRESS
    sequence = fields.Integer(string="Sequence", default=10)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade')
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    contact_ids = fields.One2many('hr.employee.emergency', 'employee_id', string='Training')