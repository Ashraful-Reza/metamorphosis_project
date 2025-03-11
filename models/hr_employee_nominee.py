from odoo import models, fields, api

class HrEmployeeNominee(models.Model):
    _name = 'hr.employee.nominee'
    _description = 'Employee Nominee'
    _order = 'sequence, id'
    
    name = fields.Char(string="Name", required=True)
    relation = fields.Char(string="Relation", required=True)
    address = fields.Text(string="Address")
    birth_date = fields.Date(string="Birth Date")
    photo = fields.Binary(string="Photo", attachment=True)
    sequence = fields.Integer(string="Sequence", default=10)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade')
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    nominee_ids = fields.One2many('hr.employee.nominee', 'employee_id', string='Nominees')