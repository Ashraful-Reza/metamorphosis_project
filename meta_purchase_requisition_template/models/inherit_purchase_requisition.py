# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseRequisitionInherit(models.Model):
    _inherit = 'purchase.requisition'

    type_id = fields.Many2one('purchase.requisition.type', string="Agreement Type", required=False, default=False)
    requisition_type = fields.Selection([
        ('blanket_order', 'Blanket Order'), ('purchase_template', 'Purchase Template')],
        string='Agreement Type', required=True, default='blanket_order')

    @api.onchange('vendor_id')
    def _onchange_vendor(self):
        self = self.with_company(self.company_id)
        if not self.vendor_id:
            self.currency_id = self.env.company.currency_id.id
        else:
            self.currency_id = self.vendor_id.property_purchase_currency_id.id or self.env.company.currency_id.id

        requisitions = self.env['purchase.requisition'].search([
            ('vendor_id', '=', self.vendor_id.id),
            ('state', '=', 'ongoing'),
            ('requisition_type', '=', 'blanket_order'),
            ('company_id', '=', self.company_id.id),
        ])
        if any(requisitions):
            title = _("Warning for %s", self.vendor_id.name)
            message = _(
                "There is already an open blanket order for this supplier. We suggest you complete this open blanket order, instead of creating a new one.")
            warning = {
                'title': title,
                'message': message
            }
            return {'warning': warning}

    @api.model_create_multi
    def create(self, vals_list):
        defaults = self.default_get(['requisition_type', 'company_id'])
        for vals in vals_list:
            requisition_type = vals.get('requisition_type', defaults['requisition_type'])
            company_id = vals.get('company_id', defaults['company_id'])
            if requisition_type == 'blanket_order':
                vals['name'] = self.env['ir.sequence'].with_company(company_id).next_by_code(
                    'purchase.requisition.blanket.order')
            else:
                vals['name'] = self.env['ir.sequence'].with_company(company_id).next_by_code(
                    'purchase.requisition.purchase.template')
        return super().create(vals_list)

    def write(self, vals):
        requisitions_to_rename = self.env['purchase.requisition']
        if 'requisition_type' in vals or 'company_id' in vals:
            requisitions_to_rename = self.filtered(lambda r:
                r.requisition_type != vals.get('requisition_type', r.requisition_type) or
                r.company_id.id != vals.get('company_id', r.company_id.id))
        res = super().write(vals)
        for requisition in requisitions_to_rename:
            if requisition.state != 'draft':
                raise UserError(_("You cannot change the Agreement Type or Company of a not draft purchase agreement."))
            if requisition.requisition_type == 'purchase_template':
                requisition.date_end = False
            code = requisition.requisition_type == 'blanket_order' and 'purchase.requisition.blanket.order' or 'purchase.requisition.purchase.template'
            requisition.name = self.env['ir.sequence'].with_company(requisition.company_id).next_by_code(code)
        return res

    def action_in_progress(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("You cannot confirm agreement '%s' because there is no product line.", self.name))
        if self.requisition_type == 'blanket_order':
            for requisition_line in self.line_ids:
                if requisition_line.price_unit <= 0.0:
                    raise UserError(_('You cannot confirm the blanket order without price.'))
                if requisition_line.product_qty <= 0.0:
                    raise UserError(_('You cannot confirm the blanket order without quantity.'))
                requisition_line.create_supplier_info()
            # self.write({'state': 'ongoing'})
        # else:
        self.write({'state': 'in_progress'})
        # Set the sequence number regarding the requisition type
        # if self.name == 'New':
        #     self.name = self.env['ir.sequence'].with_company(self.company_id).next_by_code('purchase.requisition.blanket.order')


class InheritPurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    price_unit = fields.Float(
        string='Unit Price', digits='Product Price', default=0.0,
        compute="_compute_price_unit", readonly=False, store=True)

    @api.depends('product_id', 'company_id', 'product_qty', 'product_uom_id',
                 'requisition_id.vendor_id', 'requisition_id.requisition_type')
    def _compute_price_unit(self):
        for line in self:
            if line.requisition_id.state != 'draft' or line.requisition_id.requisition_type != 'purchase_template' or not line.requisition_id.vendor_id or not line.product_id:
                continue
            current_date = fields.Date.today()
            seller = line.product_id._select_seller(
                partner_id=line.requisition_id.vendor_id, quantity=line.product_qty,
                # date=line.requisition_id.ordering_date, uom_id=line.product_uom_id)
                date=current_date, uom_id=line.product_uom_id)
            line.price_unit = seller.price if seller else line.product_id.standard_price

    def create_supplier_info(self):
        purchase_requisition = self.requisition_id
        if purchase_requisition.requisition_type == 'blanket_order' and purchase_requisition.vendor_id:
            # create a supplier_info only in case of blanket order
            self.env['product.supplierinfo'].sudo().create({
                'partner_id': purchase_requisition.vendor_id.id,
                'product_id': self.product_id.id,
                'product_tmpl_id': self.product_id.product_tmpl_id.id,
                'price': self.price_unit,
                'currency_id': self.requisition_id.currency_id.id,
                'purchase_requisition_line_id': self.id,
            })

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line, vals in zip(lines, vals_list):
            if line.requisition_id.requisition_type == 'blanket_order' and line.requisition_id.state not in ['draft', 'cancel', 'done']:
                if vals['price_unit'] <= 0.0:
                    raise UserError(_("You cannot have a negative or unit price of 0 for an already confirmed blanket order."))

                supplier_infos = self.env['product.supplierinfo'].search([
                    ('product_id', '=', vals.get('product_id')),
                    ('partner_id', '=', line.requisition_id.vendor_id.id),
                ])
                if not any(s.purchase_requisition_id for s in supplier_infos):
                    line.create_supplier_info()

        return lines

    def write(self, vals):
        res = super(InheritPurchaseRequisitionLine, self).write(vals)
        if 'price_unit' in vals:
            if vals['price_unit'] <= 0.0 and any(
                requisition.requisition_type == 'blanket_order' and
                requisition.state not in ['draft', 'cancel', 'done'] for requisition in self.mapped('requisition_id')):
                raise UserError(_('You cannot confirm the blanket order without price.'))
            # If the price is updated, we have to update the related SupplierInfo
            self.supplier_info_ids.write({'price': vals['price_unit']})
        return res


class InheritPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    requisition_type = fields.Selection(related='requisition_id.requisition_type')

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        self = self.with_company(self.company_id)
        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_company(self.company_id)._get_fiscal_position(partner)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id
        self.company_id = requisition.company_id.id
        self.currency_id = requisition.currency_id.id

        self.categ_id = requisition.product_category.id

        if not self.origin or requisition.name not in self.origin.split(', '):
            if self.origin:
                if requisition.name:
                    self.origin = self.origin + ', ' + requisition.name
            else:
                self.origin = requisition.name
        self.notes = requisition.description
        if requisition.ordering_date:
            # self.date_order = max(fields.Datetime.now(), fields.Datetime.to_datetime(requisition.ordering_date))
            self.date_order = fields.Datetime.now()
        else:
            self.date_order = fields.Datetime.now()

        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context(
                lang=partner.lang or self.env.user.lang,
                partner_id=partner.id
            )
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            taxes_ids = fpos.map_tax(
                line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids

            # Compute quantity and price_unit
            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            if requisition.requisition_type != 'purchase_template':
                product_qty = 0

            # Create PO line
            order_line_values = line._prepare_purchase_order_line(
                name=name, product_qty=product_qty, price_unit=price_unit,
                taxes_ids=taxes_ids)
            order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines

