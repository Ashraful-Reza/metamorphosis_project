from odoo import models, fields, api

class HrResumeLine(models.Model):
    _inherit = 'hr.resume.line'
    
    # Add the two new fields directly to the hr.resume.line model
    salary = fields.Float(string="salary", help="Salary for previous employment")
    class_division = fields.Char(string="class/Division", help="Class or Division achieved in education")
    # Add a computed field to get the line type name for domain conditions
    
    departure_reason_id = fields.Many2one(
        'hr.departure.reason', 
        string="Departure Reason",
        help="Reason for leaving the company"
    )
    
    @api.depends('line_type_id')
    def _compute_line_type_id_name(self):
        for record in self:
            record.line_type_id_name = record.line_type_id.name if record.line_type_id else False
    
    line_type_id_name = fields.Char(
        string="Line Type Name", 
        compute="_compute_line_type_id_name", 
        store=True,
        help="Technical field used for conditional display"
    )