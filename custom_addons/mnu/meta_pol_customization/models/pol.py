# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class PurchaseOrderX(models.Model):
    _inherit = "purchase.order"


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    qty_available = fields.Float(
        related='product_id.qty_available',
        string='Available',
        readonly=True
    )

    def action_view_stock_details(self):
        self.ensure_one()
        tree_view_id = self.env.ref('meta_pol_customization.view_stock_quant_location_tree').id
        action = {
            'name': 'Stock by Location',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'stock.quant',
            'domain': [
                ('product_id', '=', self.product_id.id),
                ('location_id.usage', '=', 'internal'),
                ('quantity', '>', 0)
            ],
            'context': {'create': False, 'edit': False, 'delete': False},
            'views': [(tree_view_id, 'tree')],
            'target': 'new',
        }
        return action

