from odoo import fields,models,api,_
import logging

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    @api.model
    def _default_sale_id(self):
        """Set the default sale order based on the origin of the mrp.production record."""
        # for rec in self:
        if self.origin:
            sale_order = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
            logging.info(f"Sale Order From MRP Production---------------->{sale_order}")
            return sale_order.id if sale_order else None
        else:
            return None

    sale_id=fields.Many2one(comodel_name="sale.order",string="Sale Order",default=_default_sale_id)
    part_no=fields.Char(string="Part No.")
