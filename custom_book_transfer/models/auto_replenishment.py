# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.tools.misc import clean_context
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)

class AutoReplenishmentProcess(models.Model):
    _name = 'auto.replenishment.process'
    _description = 'Intelligent Transfer and Replenishment Management'

    def _run_automatic_replenishment(self):
        with self.env.cr.savepoint():
            try:
                # Find the main source warehouse (primary resupply warehouse)
                source_warehouse = self.env['stock.warehouse'].search([
                    ('buy_to_resupply', '=', True),
                    ('active', '=', True),
                    ('company_id', '=', self.env.company.id),
                    ('lot_stock_id', '!=', False)
                ], limit=1)

                if not source_warehouse:
                    _logger.error("No primary resupply warehouse found!")
                    return

                # Find secondary warehouses with resupply enabled - FIXED LINE
                secondary_warehouses = self.env['stock.warehouse'].search([
                    ('id', '!=', source_warehouse.id),
                    ('active', '=', True),
                    # Check for non-empty resupply_wh_ids
                    ('resupply_wh_ids', '!=', False)
                ])

                replenishment_log = []

                # Iterate through secondary warehouses
                for dest_warehouse in secondary_warehouses:
                    # Find products with reordering rules for this warehouse
                    reordering_rules = self.env['stock.warehouse.orderpoint'].search([
                        ('warehouse_id.id', '=', dest_warehouse.id),
                        ('active', '=', True)
                    ])

                    for rule in reordering_rules:
                        product = rule.product_id

                        try:
                            # Calculate current stock in destination warehouse
                            dest_stock = self._get_product_stock(product, dest_warehouse)

                            # Log stock information for debugging
                            _logger.info(f"Product: {product.name}, Dest Warehouse: {dest_warehouse.name}, Current Stock: {dest_stock}, Min Qty: {rule.product_min_qty}")

                            # Check if stock is below minimum reordering quantity
                            if float_compare(dest_stock, rule.product_min_qty, precision_rounding=product.uom_id.rounding) <= 0:
                                # Determine quantity to replenish
                                qty_to_replenish = max(
                                    rule.product_max_qty - dest_stock,
                                    rule.product_min_qty - dest_stock
                                )

                                # Ensure positive replenishment quantity
                                qty_to_replenish = max(qty_to_replenish, 0)

                                # Check for existing replenishment orders
                                needed_qty = self._check_existing_replenishment(product, dest_warehouse, qty_to_replenish)

                                # Skip if no additional replenishment is needed
                                if needed_qty <= 0:
                                    _logger.info(f"No additional replenishment needed for {product.name} in {dest_warehouse.name} - already in progress")
                                    continue

                                # Update qty_to_replenish with the quantity still needed
                                qty_to_replenish = needed_qty

                                # Check stock in source warehouse
                                source_stock = self._get_product_stock(product, source_warehouse)

                                replenishment_methods = []

                                # Determine transfer quantity
                                transfer_qty = qty_to_replenish

                                # Calculate purchase quantity needed
                                purchase_needed_qty = max(0, qty_to_replenish - source_stock)

                                # Only attempt transfer if there's quantity to transfer and source has stock
                                if transfer_qty > 0 and source_stock > 0:
                                    transfer_qty_actual = min(transfer_qty, source_stock)

                                    try:
                                        # Get the resupply route between warehouses
                                        resupply_routes = dest_warehouse.resupply_route_ids.filtered(
                                            lambda r: source_warehouse in r.supplied_wh_id and r.supplier_wh_id in r.warehouse_ids
                                        )

                                        # Get the appropriate route or default route
                                        route = None
                                        if product.route_ids:
                                            # First try to find product specific resupply routes
                                            product_routes = product.route_ids.filtered(
                                                lambda r: source_warehouse in r.supplied_wh_id and r.supplier_wh_id in r.warehouse_ids
                                            )
                                            if product_routes:
                                                route = product_routes[0]

                                        # If no product specific route, use warehouse resupply route
                                        if not route and resupply_routes:
                                            route = resupply_routes[0]

                                        if not route:
                                            _logger.error(f"No resupply route found between warehouses for product {product.name}")
                                            continue

                                        # Create a reference for the replenishment
                                        reference = f"AUTO-REPL-{dest_warehouse.id}-{source_warehouse.id}"

                                        # Now use the procurement system like launch_replenishment
                                        # Record current time to find created moves later for notification
                                        now = self.env.cr.now()

                                        # Convert quantity to product's UOM if needed
                                        uom_reference = product.uom_id

                                        # Create a replenishment group - similar to the manual method
                                        replenishment = self.env['procurement.group'].create({
                                            'name': f"Auto Replenishment {dest_warehouse.name}",
                                            'move_type': 'direct',
                                        })

                                        # Prepare values similar to _prepare_run_values in ProductReplenish
                                        values = {
                                            'warehouse_id': dest_warehouse,
                                            'route_ids': route,
                                            'date_planned': fields.Datetime.now() + timedelta(days=1),  # Next day delivery
                                            'group_id': replenishment,
                                        }

                                        # Run the procurement - this is the key method from launch_replenishment
                                        self.env['procurement.group'].with_context(
                                            clean_context(self.env.context)
                                        ).run([
                                            self.env['procurement.group'].Procurement(
                                                product,
                                                transfer_qty_actual,
                                                uom_reference,
                                                dest_warehouse.lot_stock_id,  # Destination location
                                                f"Auto Replenishment: {reference}",  # Name
                                                reference,  # Origin
                                                dest_warehouse.company_id,
                                                values  # Values with route, date, etc.
                                            )
                                        ])

                                        # Find moves that were created by this procurement for logging
                                        moves = self.env['stock.move'].search([
                                            ('create_date', '>=', now),
                                            ('product_id', '=', product.id),
                                            ('origin', '=', reference)
                                        ])

                                        if moves:
                                            pickings = moves.mapped('picking_id')
                                            for picking in pickings:
                                                _logger.info(f"Created picking {picking.name} for {product.name} with reference {reference}")

                                        # Add to replenishment methods for logging
                                        replenishment_methods.append({
                                            'method': 'internal_transfer',
                                            'quantity': transfer_qty_actual,
                                            'moves': len(moves),
                                            'reference': reference
                                        })

                                    except Exception as transfer_error:
                                        _logger.error(f"Transfer error for {product.name}: {str(transfer_error)}")
                                        self._create_error_log(product, f"Transfer error: {str(transfer_error)}")

                                # If there's still remaining quantity or no source stock, consider purchase order
                                if purchase_needed_qty > 0:
                                    # Find suitable vendors
                                    vendors = self._get_suitable_vendors(product, purchase_needed_qty)
                                    _logger.info(f"Creating PO for warehouse: {source_warehouse.name}, ID: {source_warehouse.id}")
                                    if vendors:
                                        # Create or update purchase order
                                        purchase_order = self._create_purchase_order(
                                            product,
                                            purchase_needed_qty,
                                            source_warehouse,  # Use source warehouse for purchase
                                            rule,
                                            vendors[0]
                                        )

                                        if purchase_order:
                                            replenishment_methods.append({
                                                'method': 'purchase_order',
                                                'quantity': purchase_needed_qty
                                            })
                                            _logger.info(f"Created PO: {purchase_order.name} for warehouse: {purchase_order.picking_type_id.warehouse_id.name}")

                                # Log replenishment details
                                if replenishment_methods:
                                    log_message = f"Replenishment for {product.name} in {dest_warehouse.name}:"
                                    for method in replenishment_methods:
                                        if method['method'] == 'internal_transfer':
                                            log_message += f"\n - Internal Transfer: {method['quantity']} {product.uom_id.name} "
                                            if 'moves' in method:
                                                log_message += f" ({method['moves']} moves created)"
                                        else:
                                            log_message += f"\n - Purchase Order: {method['quantity']} {product.uom_id.name} (Reference: {method['reference']})"

                                    _logger.info(log_message)
                                    replenishment_log.append(log_message)

                        except Exception as e:
                            _logger.error(f"Replenishment error for {product.name}: {str(e)}")
                            self._create_error_log(product, str(e))

                # Log replenishment summary
                if replenishment_log:
                    _logger.info("Replenishment Summary:\n" + "\n".join(replenishment_log))

            except Exception as main_error:
                _logger.error(f"Critical error in replenishment process: {str(main_error)}")
                self._create_error_log(None, f"Critical replenishment process error: {str(main_error)}")

    def _check_existing_replenishment(self, product, warehouse, qty_to_replenish):
        """
        Check if there are already purchase orders or transfers in progress
        that will satisfy this replenishment need
        """
        rule = self.env['stock.warehouse.orderpoint'].search([
            ('warehouse_id', '=', warehouse.id),
            ('product_id', '=', product.id),
            ('active', '=', True)
        ], limit=1)

        if not rule:
            return qty_to_replenish

        # Check existing incoming transfer orders for this warehouse
        move_lines = self.env['stock.move'].search([
            ('product_id', '=', product.id),
            ('state', 'in', ['draft', 'waiting', 'assigned', 'confirmed']),
            ('location_dest_id', '=', warehouse.lot_stock_id.id)
        ])

        # Check existing purchase orders for this product
        po_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', product.id),
            ('state', 'in', ['draft', 'sent', 'to approve'])
            # ('order_id.origin', 'like', f'AUTO/REPL/%')
        ])
        _logger.info(f"Searching for all PO lines for product: {product.name} (ID: {product.id})")
        for po_line in po_lines:
            _logger.info(f"Found PO: {po_line.order_id.name}, Qty: {po_line.product_qty}, State: {po_line.order_id.state}")
        # Sum quantities from transfer lines
        current_transfer_qty = sum(move_lines.mapped('product_uom_qty'))
        current_po_qty = sum(po_lines.mapped('product_qty'))
        total_incoming = current_transfer_qty + current_po_qty

        # Get the max quantity from the rule
        max_qty = rule.product_max_qty
        # Calculate how much is already covered by existing transfers
        current_stock = self._get_product_stock(product, warehouse)
        total_expected = current_stock + total_incoming

        _logger.info(f"Product: {product.name}")
        _logger.info(f"Current Stock: {current_stock}")
        _logger.info(f"Current Transfer Qty: {current_transfer_qty}")
        _logger.info(f"Current PO Qty: {current_po_qty}")
        _logger.info(f"Total Expected: {total_expected}")
        _logger.info(f"Max Qty: {max_qty}")
        _logger.info(f"Qty to Replenish: {qty_to_replenish}")

        # If the total expected quantity already meets or exceeds max_qty, no more is needed
        if total_expected >= max_qty:
            _logger.info(f"Existing transfers/POs already meet or exceed max qty {max_qty}")
            return 0

        # Calculate how much more is needed to reach max quantity
        additional_needed = max_qty - total_expected
        # Ensure we don't exceed the max qty
        qty_to_update = min(qty_to_replenish, additional_needed)

        _logger.info(f"Additional Needed: {additional_needed}")
        _logger.info(f"Qty to Update: {qty_to_update}")

        # Update existing transfer lines if they exist
        if move_lines:
            for move in move_lines:
                old_qty = move.product_uom_qty
                new_qty = move.product_uom_qty + qty_to_update
                move.write({'product_uom_qty': new_qty})
                _logger.info(f"Updated move {move.id} qty from {old_qty} to {new_qty}")

                # Now also update the PO line for the same product if it exists
                if po_lines:
                    for po_line in po_lines:
                        old_po_qty = po_line.product_qty
                        new_po_qty = po_line.product_qty + qty_to_update
                        po_line.write({'product_qty': new_po_qty})
                        _logger.info(f"Updated corresponding PO line {po_line.id} for product {product.name} from {old_po_qty} to {new_po_qty}")
                        break  # Update only the first PO line

                return 0  # Updated transfer, no need to continue

        # If we get here, there are no existing transfers to update
        # But we should update existing PO lines if they exist
        if po_lines:
            for po_line in po_lines:
                old_qty = po_line.product_qty
                new_qty = po_line.product_qty + qty_to_update
                po_line.write({'product_qty': new_qty})
                _logger.info(f"Updated PO line {po_line.id} for product {product.name} from {old_qty} to {new_qty}")
                break  # Update only the first PO line

        # Important: Even if we updated a PO, we still need to create a new transfer
        # So we return the additional needed quantity regardless
        return additional_needed

    def _get_product_stock(self, product, warehouse):
        """
        Get current stock level for a product in a specific warehouse
        """
        StockQuant = self.env['stock.quant']

        # Get internal location IDs for the warehouse
        locations = self.env['stock.location'].search([
            ('location_id', 'child_of', warehouse.view_location_id.id),
            ('usage', '=', 'internal')
        ])

        # If no specific internal locations found, use the warehouse stock location
        if not locations and warehouse.lot_stock_id:
            locations = warehouse.lot_stock_id

        if not locations:
            return 0.0

        # Search for quants in the warehouse locations
        quants = StockQuant.search([
            ('product_id', '=', product.id),
            ('location_id', 'in', locations.ids),
            ('quantity', '>', 0)
        ])

        # Sum available quantities
        available_qty = sum(quant.quantity for quant in quants)
        return available_qty

    def _get_suitable_vendors(self, product, quantity):
        """
        Find suitable vendors for the product based on availability and price
        """
        suppliers = self.env['product.supplierinfo'].search([
            ('product_tmpl_id', '=', product.product_tmpl_id.id),
            ('min_qty', '<=', quantity),
            '|',
            ('date_start', '=', False),
            ('date_start', '<=', fields.Date.today()),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', fields.Date.today()),
        ], order='price, min_qty')

        return suppliers

    def _create_purchase_order(self, product, quantity, warehouse, rule, supplier):
        """
        Create a purchase order for the product
        """
        PurchaseOrder = self.env['purchase.order']
        PurchaseOrderLine = self.env['purchase.order.line']

        # Check if partner exists
        if not supplier.partner_id:
            _logger.error(f"No vendor defined for product {product.name}")
            return False
        _logger.info(f"Creating PO with supplier: {supplier.partner_id.name} for product: {product.name}")
        # Create purchase order
        purchase_date = fields.Date.today()

        # Get picking type for purchases
        picking_type = warehouse.in_type_id
        _logger.info(f"Using picking type: {picking_type.name} for warehouse: {warehouse.name}")

        batch_reference = f'AUTO/REPL/{fields.Date.today()}/{warehouse.id}'

        # Create or find existing PO for this supplier
        domain = [
            ('state', '=', 'draft'),
            ('picking_type_id', '=', picking_type.id),
            ('origin', '=', batch_reference),
        ]

        order = PurchaseOrder.search(domain, limit=1)

        if not order:
            order_vals = {
                'partner_id': supplier.partner_id.id,
                'date_order': purchase_date,
                'picking_type_id': picking_type.id,
                'company_id': warehouse.company_id.id,
                'origin': batch_reference,  # Use the same reference here
            }
            order = PurchaseOrder.create(order_vals)
            _logger.info(f"Created new PO: {order.name} with ID: {order.id}")
        else:
            _logger.info(f"Found existing PO: {order.name} with ID: {order.id}")

        # Calculate scheduled date
        schedule_date = purchase_date
        if supplier.delay:
            schedule_date = fields.Date.from_string(purchase_date) + timedelta(days=supplier.delay)

        # Check for existing line for the same product
        existing_line = PurchaseOrderLine.search([
            ('order_id', '=', order.id),
            ('product_id', '=', product.id),
            ('state', '=', 'draft')
        ], limit=1)

        if existing_line:
            # Update quantity of existing line
            existing_line.write({
                'product_qty': existing_line.product_qty + quantity
            })
        else:
            # Create purchase order line
            _logger.info(f"Creating new PO line for product {product.name} with qty {quantity}")
            line_vals = {
                'order_id': order.id,
                'product_id': product.id,
                'product_qty': quantity,
                'product_uom': product.uom_po_id.id,
                'price_unit': supplier.price,
                'date_planned': schedule_date,
                'name': f"{product.name} (Auto Replenishment)"
            }

            po_line = PurchaseOrderLine.create(line_vals)
            _logger.info(f"Created PO line with ID: {po_line.id}")
        _logger.info(f"Successfully created/updated PO: {order.name} for product: {product.name} with qty: {quantity}")
        return order

    def _create_error_log(self, product, error_message):
        """
        Create an error log record for tracking replenishment failures
        """
        try:
            # Check if model exists first
            if self.env['ir.model'].search([('model', '=', 'auto.replenishment.error')]):
                # Create error log with proper error handling
                error_log = self.env['auto.replenishment.error'].create({
                    'product_id': product.id if product else None,
                    'error_message': str(error_message),
                    'error_date': fields.Datetime.now(),
                })
                return error_log
            else:
                # Just log to logger if model doesn't exist
                _logger.error(f"Error log model not found: {str(error_message)}")
                return False
        except Exception as log_error:
            # Fallback logging if error creation fails
            _logger.error(f"Failed to create error log: {str(log_error)}")
            return False

class AutoReplenishmentError(models.Model):
    _name = 'auto.replenishment.error'
    _description = 'Auto Replenishment Error Log'
    _order = 'error_date desc'

    product_id = fields.Many2one('product.product', string='Product', index=True)
    error_message = fields.Text(string='Error Message', required=True)
    error_date = fields.Datetime(string='Error Date', default=fields.Datetime.now, required=True)
    resolved = fields.Boolean(string='Resolved', default=False)
    resolution_note = fields.Text(string='Resolution Note')
