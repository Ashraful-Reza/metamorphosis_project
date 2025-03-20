from odoo import models,api # type: ignore

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_print_contact_pdf(self):
        return self.env.ref('contact_pdf_print.action_report_contact').report_action(self)