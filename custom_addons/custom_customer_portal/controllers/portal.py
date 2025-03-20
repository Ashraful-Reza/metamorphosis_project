from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import AND

class MySalesOrderPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        SaleOrder = request.env['sale.order']
        
        if 'sales_counts' in counters:
            domain = [
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['sale', 'done'])
            ]
            values['sales_counts'] = SaleOrder.search_count(domain) if SaleOrder.check_access_rights('read', raise_exception=False) else 0
            
        return values
    
    @http.route(['/sales/order', '/sales/order/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_sales_orders(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']
        
        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done'])
        ]
        
        # Search filters
        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        
        # Default sort by order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']
        
        # Search
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search in Orders')},
            'name': {'input': 'name', 'label': _('Search in Reference')},
        }
        
        # Search domain
        search_domain = []
        if search and search_in:
            if search_in == 'name':
                search_domain = [('name', 'ilike', search)]
            else:
                search_domain = ['|', ('name', 'ilike', search), ('partner_id.name', 'ilike', search)]
            
        if search_domain:
            domain = AND([domain, search_domain])
            
        # Date range filter
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
            
        # Count for pager
        order_count = SaleOrder.search_count(domain)
        
        # Pager
        pager = portal_pager(
            url="/sales/order",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in, 'search': search},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        
        # Content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_sales_history'] = orders.ids[:100]
        
        values.update({
            'date': date_begin,
            'orders': orders,
            'page_name': 'sales_orders',
            'pager': pager,
            'default_url': '/sales/order',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
        })
        
        # Create or use existing template
        return request.render("sale.portal_my_orders", values)