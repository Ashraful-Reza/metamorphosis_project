from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    childrenn_ids = fields.One2many('hr.employee.childrenn', 'employee_id', string='Childrenns')
    def action_report_employee_profile(self):
        return self.env.ref('employee_profile_pdf_print.action_report_employee_profile').report_action(self)
