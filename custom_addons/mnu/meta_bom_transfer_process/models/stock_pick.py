# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command
import logging

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.model
    def _default_sale_id(self):
        """Set the default sale order based on the origin of the mrp.production record."""
        # for rec in self:
        if self.origin:
            sale_order = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
            logging.info(f"Sale Order For Stock Picking---------------->{sale_order}")
            return sale_order.id if sale_order else None
        
        elif self.production_id and self.production_id.sale_id:
            return self.production_id.sale_id  

        else:
            return None
    

    is_bom_product = fields.Boolean(string='Is Bom Product Transfer', default=False)
    # is_internal = fields.Boolean(string='Is Internal Transfer', default=find_is_internal)
    is_mo_product = fields.Boolean(string='Manufacture Product Transfer', default=False)
    product_tmpl_id = fields.Many2one(comodel_name='product.template', string='Bom Product',domain="[('bom_ids', '!=', False)]")
    product_qty = fields.Float(string='Product Quantity',default=1.0)

    bom_id = fields.Many2one(comodel_name='mrp.bom', string='Bill of Materials',help='Select the Bill of Materials for the chosen product.')
    production_id = fields.Many2one(comodel_name='mrp.production', string='Manufacturing Order')
    production_bom_id = fields.Many2one(comodel_name='mrp.bom', string='MO Bill of Materials',help='Select the Bill of Materials for the chosen product.')
    sale_id=fields.Many2one(comodel_name="sale.order",string="Sale Order",default=_default_sale_id)
    part_no=fields.Char(string="Part No.")
    vendor_reference=fields.Char(string="Vendor Reference",related='purchase_id.partner_ref')


    # @api.onchange('production_id','bom_id','is_bom_product','is_mo_product','state')
    # def _onchange_production_id(self):   
    #     # Reset BOM and product template when production changes
    #     if self.is_mo_product and self.state not in ['done']:
    #         logging.info(f"is_mo_product-------***>{self.is_mo_product}")
    #         if self.production_id:
    #             logging.info(f"self.production_id-------***>{self.production_id}")
    #             self.product_qty=self.production_id.product_qty
    #             self.bom_id = self.production_id.bom_id
    #             logging.info(f"self.bom_id-------***>{self.bom_id}")
    #             self.add_move_data(self.bom_id)
    #         else:
    #             self.bom_id = False
    #             self.product_qty = 0.0
    #             self.clear_move_data()

    #     elif self.is_bom_product and self.state not in ['done']:
    #         if self.bom_id:
    #             logging.info(f"self.bom_id from is_bom_product-------***>{self.bom_id}")
    #             self.add_move_data(self.bom_id)
    #         else:
    #             self.bom_id = False
    #             self.clear_move_data()
    #     else:
    #         if self.state not in ['done']:
    #             self.bom_id = False
    #             self.production_id = False
    #             self.product_qty = 0.0
    #             self.clear_move_data()        
    
    # def clear_move_data(self):        
    #     for move in self.move_ids:
    #         move.unlink()

    #     # self.move_ids = [Command.clear()]


    # def add_move_data(self,bom):
    #     self.clear_move_data()  # Clear existing moves before adding new ones
    #     moves_to_add = [Command.create({"product_id":False, "product_uom_qty":0})]
    #     if bom:
    #         logging.info(f"Number of Bom Lines :-------------******>{len(bom.bom_line_ids)}")
    #         for line in bom.bom_line_ids:
    #             product_uom_qty = ((line.product_qty*self.product_qty)/bom.product_qty) if self.product_qty>0 else (line.product_qty/bom.product_qty)
                
    #             logging.info(f"Bom Line :-------------******>{line.product_id.id}")
    #             move = {
    #                 'name': line.product_id.display_name,
    #                 'date': self.scheduled_date,
    #                 'product_uom_qty': product_uom_qty,
    #                 'location_dest_id': self.location_dest_id.id,
    #                 'location_id': self.location_id.id,
    #                 'product_id': line.product_id.id,
    #                 'product_uom': line.product_uom_id.id,
    #                 'picking_id': self._origin.id if self._origin.id else self.id,
    #                 'bom_line_id': line.id,
    #                 'company_id':self.company_id.id,

    #             }
    #             moves_to_add.append(Command.create(move))
    #             logging.info(f"Move Added For :--------------*******>{move}")
    #             # self.move_ids = [Command.create(move)]

    #             # st_move=self.write({'move_ids': [(0, 0, move)]})
    #             # logging.info(f"Move Added For ID:--------------*******>{st_move}")
    #             # self.move_ids_without_package+=[(0, 0, move)]
        
    #     logging.info(f"appended Move :--------------*******>{moves_to_add}")
    #     if moves_to_add:
    #         self.move_ids = moves_to_add
    #     logging.info(f"self.move_ids ##################### {self.move_ids}")

    # def open_btw_wizard(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Select BOM',
    #         'res_model': 'bom.transfer.wizard',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {'active_model': self._name, 'active_ids': self.ids},
    #     }