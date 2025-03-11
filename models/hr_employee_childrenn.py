from odoo import models, fields, api

class HrEmployeeChildrenn(models.Model):
    _name = 'hr.employee.childrenn'
    _description = 'Employee Childrenn'
    _order = 'sequence, id'
    
    name = fields.Char(string="Name", required=True)
    birth_date = fields.Date(string="Birth Date")
    photo = fields.Binary(string="Photo", attachment=True)
    sequence = fields.Integer(string="Sequence", default=10)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade')

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    children_ids = fields.One2many('hr.employee.childrenn', 'employee_id', string='Childrens')

