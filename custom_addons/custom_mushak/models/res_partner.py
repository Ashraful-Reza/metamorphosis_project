from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    bin_id = fields.Char(string='BIN ID', help='Bangladesh Tax Identification Number (BIN)')