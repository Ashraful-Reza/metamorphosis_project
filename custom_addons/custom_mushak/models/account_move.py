from odoo import models

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_print_mushak(self):
        return self.env.ref('mushak_invoice_report.mushak_invoice_report')
