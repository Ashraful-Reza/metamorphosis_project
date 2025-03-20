from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleDiscountApproval(models.TransientModel):
    _name = "sale.discount.approval"
    _description = "Sales Order Discount Approval"

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True)
    discount_reason = fields.Text(string="Reason for Approval", required=True)

    def action_approve_discount(self):
        """ Approve the discount and confirm the sales order """
        if not self.discount_reason:
            raise UserError("Please provide a reason for the discount approval.")
        
        self.sale_order_id.write({
            'discount_approved': True,
            'discount_reason': self.discount_reason
        })
        return {'type': 'ir.actions.act_window_close'}