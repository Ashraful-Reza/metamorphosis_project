# -*- coding: utf-8 -*-
{
    'name': 'Custom Book Transfer',
    
    'summary': 'Customized replenishment rules for consolidating transfer orders',
    'description': """
        This module customizes the default replenishment behavior:
        - Consolidates transfer orders with the same reference number
        - Increases quantity for existing products in active transfers
        - Adds new products to existing transfers for the same warehouse
        - Works with transfers in draft, waiting and ready states
    """,

    'author':"Metamorphosis Ltd, Tanjil",
    'co-author':"Tanjil",
    'website':'https://metamorphosis.com.bd',

    'version': '18.0.0.1',
    'category': 'Tools/Tools',
    'license': 'AGPL-3',

    'depends': ['stock','base', 'sale','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/scheduler_data.xml',
        # 'views/auto_replenishment_error_view.xml',
    ],

     'sequence':-120,
    "installable": True,
    "application": True,
    'auto_install': False,
}
