from odoo import http
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import CustomerPortal

from odoo.http import request
import re

class CustomPortal(portal.CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        
        values['order_count'] = request.env['sale.order'].search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done'])
        ])
        
        values['invoice_count'] = request.env['account.move'].search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', 'not in', ['draft', 'cancel'])
        ])
        
        values['vendor_invoice_count'] = request.env['account.move'].search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('move_type', 'in', ['in_invoice', 'in_refund']),
            ('state', 'not in', ['draft', 'cancel'])
        ])
        
        return values

    @http.route(['/my/home', '/my'], type='http', auth="user", website=True)
    def home(self, **kw):
        """Override the portal home route to inject our badges"""
        # Call the original method to get the standard response
        response = super(CustomPortal, self).home(**kw)
        
        if hasattr(response, 'render'):
            # Get the HTML content
            html = response.render()
            
            # Get the counts
            values = self._prepare_home_portal_values(['order_count', 'invoice_count', 'vendor_bill_count'])
            order_count = values.get('order_count', 0)
            invoice_count = values.get('invoice_count', 0)
            vendor_invoice_count = values.get('vendor_invoice_count', 0)
            
            # Create badge HTML for each count
            order_badge = f'<span class="badge rounded-pill text-bg-primary" style="position: absolute; right: 15px; top: 50%; transform: translateY(-50%);">{order_count}</span>'
            invoice_badge = f'<span class="badge rounded-pill text-bg-primary" style="position: absolute; right: 15px; top: 50%; transform: translateY(-50%);">{invoice_count}</span>'
            vendor_badge = f'<span class="badge rounded-pill text-bg-primary" style="position: absolute; right: 15px; top: 50%; transform: translateY(-50%);">{vendor_invoice_count}</span>'
            
            # Inject badges into links
            if order_count > 0:
                html = re.sub(
                    r'(<a[^>]*href="[^"]*\/my\/orders[^"]*"[^>]*>)(.*?<\/a>)',
                    r'\1' + order_badge + r'\2',
                    html,
                    flags=re.DOTALL
                )
            
            if invoice_count > 0:
                html = re.sub(
                    r'(<a[^>]*href="[^"]*\/my\/invoices[^"]*"[^>]*>)(.*?<\/a>)',
                    r'\1' + invoice_badge + r'\2',
                    html,
                    flags=re.DOTALL
                )
            
            if vendor_invoice_count > 0:
                html = re.sub(
                    r'(<a[^>]*href="[^"]*\/my\/bills[^"]*"[^>]*>)(.*?<\/a>)',
                    r'\1' + vendor_badge + r'\2',
                    html,
                    flags=re.DOTALL
                )
            
            # Make sure links have relative positioning
            html = re.sub(
                r'(<a[^>]*href="[^"]*\/my\/(orders|invoices|bills)[^"]*")',
                r'\1 style="position: relative;"',
                html
            )
            
            # Return modified response
            return http.Response(html, mimetype='text/html')
        
        return response