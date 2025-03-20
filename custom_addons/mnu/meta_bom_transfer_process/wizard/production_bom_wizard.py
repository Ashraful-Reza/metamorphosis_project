from odoo import models, fields, api, Command
import logging


class BomTransferWizard(models.TransientModel):
    _name = "bom.transfer.wizard"
    _description = "BOM Transfer Wizard"

    location_id = fields.Many2one(
        "stock.location",
        "Source Location",
        readonly=False,
        required=True,
        domain='[("usage", "=", "internal")]',
    )
    location_dest_id = fields.Many2one(
        "stock.location",
        "Destination Location",
        readonly=False,
        required=True,
        domain='[("usage", "=", "internal")]',
    )
    scheduled_date = fields.Datetime(
        string="Scheduled Date", default=fields.Datetime.now
    )
    picking_type_id = fields.Many2one(
        "stock.picking.type",
        "Operation Type",
        readonly=False,
        required=True,
        domain='[("code", "=", "internal")]',
    )

    is_bom_product = fields.Boolean(string="Is Bom Product Transfer", default=False)
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Bill of Materials",
        help="Select the Bill of Materials for the chosen product.",
    )

    is_mo_product = fields.Boolean(string="Manufacture Product Transfer", default=False)
    production_id = fields.Many2one(
        comodel_name="mrp.production", string="Manufacturing Order"
    )
    production_bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="MO Bill of Materials",
        help="Select the Bill of Materials for the chosen product.",
    )
    product_qty = fields.Float(string="Product Quantity", default=1.0)

    bom_lines = fields.One2many(
        comodel_name="bom.transfer.wizard.line",
        inverse_name="wizard_id",
        string="BOM Lines",
        compute="_compute_bom_lines"
    )

    @api.depends(
        "production_id", "bom_id", "is_bom_product", "is_mo_product", "product_qty"
    )
    def _compute_bom_lines(self):
        # Reset BOM and product template when production changes
        # self.clear_bom_lines()
        if self.picking_type_id and self.scheduled_date and self.location_dest_id and self.location_id:
            if self.is_mo_product and self.production_id:
                # self.product_qty=self.production_id.product_qty
                self.production_bom_id = self.production_id.bom_id
                self.bom_lines = self._get_bom_lines(self.production_bom_id)

            elif self.is_bom_product and self.bom_id:
                logging.info(f"self.bom_id from is_bom_product-------***>{self.bom_id}")
                self.bom_lines = self._get_bom_lines(self.bom_id)
            else:
                self.bom_lines = False
        else:
            # self.bom_id = False
            # self.production_id = False
            # self.product_qty = 0.0
            # self.clear_bom_lines()
            self.bom_lines = False
            pass

    def clear_bom_lines(self):
        # if self.bom_lines:
        #     for move in self.bom_lines:
        #         move.unlink()
        # else:
        #     pass
        self.bom_lines = [Command.clear()]

    def _get_bom_lines(self, bom):
        # self.clear_bom_lines()
        bms_to_add = False
        if bom:
            bms_to_add = []
            for line in bom.bom_line_ids:
                product_uom_qty = (
                    ((line.product_qty * self.product_qty) / bom.product_qty)
                    if self.product_qty > 0
                    else (line.product_qty / bom.product_qty)
                )

                bmlines = {
                    "product_id": line.product_id.id,
                    "product_uom_qty": product_uom_qty,
                    "product_uom": line.product_uom_id.id,
                }
                bms_to_add.append(Command.create(bmlines))
                logging.info(f"BOM Lines Added For :--------------*******>{bmlines}")
        return bms_to_add

    def add_move_data_to_picking(self):
        sp_value_list = []
        for wiz in self:
            # moves_to_add = [Command.create({"product_id":False, "product_uom_qty":0})]

            # picking_type_id=self.env['stock.picking.type'].sudo().search([('code','=','internal')])
            stock_picking = self.env["stock.picking"].sudo()

            sp_value = {
                "location_dest_id": wiz.location_dest_id.id,
                "location_id": wiz.location_id.id,
                "picking_type_id": wiz.picking_type_id.id,
                "move_type": "direct",
                "scheduled_date": wiz.scheduled_date,
                "production_id": wiz.production_id.id,
                "production_bom_id": wiz.production_bom_id.id,
                "bom_id": wiz.bom_id.id,
                "product_qty": wiz.product_qty,
                "is_mo_product": wiz.is_mo_product,
                "is_bom_product": wiz.is_bom_product,
                'company_id':self.env.company.id,
                "move_ids": [],
            }

            # if created_sp.bom_id:
            #     logging.info(f"Number of Bom Lines :-------------******>{len(self.bom_id.bom_line_ids)}")
            moves_to_add = []
            for line in wiz.bom_lines:
                # product_uom_qty = ((line.product_qty*self.product_qty)/self.bom_id.product_qty) if self.product_qty>0 else (line.product_qty/self.bom_id.product_qty)
                move = {
                    "name": line.product_id.display_name,
                    "date": wiz.scheduled_date,
                    "product_uom_qty": line.product_uom_qty,
                    "location_dest_id": wiz.location_dest_id.id,
                    "location_id": wiz.location_id.id,
                    "product_id": line.product_id.id,
                    "product_uom": line.product_uom.id,
                    # 'picking_id': created_sp.id,
                    # 'bom_line_id': line.id,
                    'company_id':self.env.company.id,
                }
                # moves_to_add.append(Command.create(move))
                sp_value["move_ids"].append(Command.create(move))

        sp_value_list.append(sp_value)
        # logging.info(f"appended Move :--------------*******>{moves_to_add}")

        created_sp = stock_picking.create(sp_value_list)
        logging.info(f"self.move_ids ##################### {created_sp.name}")

        ctx = dict(self.env.context)
        action = {
            "name": "BOM Transfers",
            "view_mode": "form,tree",
            "res_model": "stock.picking",
            "res_id": created_sp.id,
            "type": "ir.actions.act_window",
            "context": ctx,
        }

        return action


class BomTransferWizardLine(models.TransientModel):
    _name = "bom.transfer.wizard.line"
    _description = "BOM Transfer Wizard Line"

    wizard_id = fields.Many2one(comodel_name="bom.transfer.wizard")
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    product_uom_qty = fields.Float(string="Demand")
    product_uom = fields.Many2one(comodel_name="uom.uom", string="Unit")
