from odoo import models, fields, api

class HrEmployeeTraining(models.Model):
    _name = 'hr.employee.training'
    _description = 'Employee Training'
    _order = 'sequence, id'
    
    training_title = fields.Char(string="Training Ttitle", required=True)
    training_year = fields.Date(string="Year")
    name = fields.Date(string="Year")
    institute = fields.Text(string="Institute")
    sequence = fields.Integer(string="Sequence", default=10)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade')
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    trn_ids = fields.One2many('hr.employee.training', 'employee_id', string='Training')