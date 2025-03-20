# -*- coding: utf-8 -*-
{
    'name': "Purchase Order Line Stock Data",

    'summary': "This Module Enables Some Features In The Purchase order Line and other related to the stock. Please See Description Of the module for details.",

    'description': """
        This module is used to customize the purchase order line. The Features Are Described Below:
            1.Will add a new field representing the overview of the stock available for all the locations.
    """,

    'author': "Metamorphosis, Rifat Anwar",
    'co-author': "Rifat Anwar",
    'website': "https://metamorphosis.com.bd",
    'category': 'Tools/Tools',
    'license': 'AGPL-3',
    'version': '17.0.0.1',

    'depends': ['purchase','stock'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/pol_view.xml',
    ],
    'sequence':-199,
    'application': True,
    'installable': True,
    'auto_install': False,
}