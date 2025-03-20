from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    discount_approved = fields.Boolean(string="Discount Approved", default=False)
    discount_reason = fields.Text(string="Discount Reason", readonly=True)

    def action_confirm(self):
        """ Override confirm method to check discount approval """
        for order in self:
            max_discount = 30  # Max discount percentage allowed
            if any(line.discount > max_discount for line in order.order_line) and not order.discount_approved:
                return {
                    'name': "Discount Approval",
                    'type': 'ir.actions.act_window',
                    'res_model': 'sale.discount.approval',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_sale_order_id': order.id},
                }
        return super(SaleOrder, self).action_confirm()
