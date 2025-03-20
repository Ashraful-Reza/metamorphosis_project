# -*- coding: utf-8 -*-
{
    'name': "Portal Customize",

    'summary': """
    Will help to view number of sales in portal.
    """,

    'description': """
    
    """,

    'maintainer': 'Metamorphosis',
    'author': "Metamorphosis,Tanjil",
    'co-author': "Tanjil",
    'website': "https://metamorphosis.com.bd/",
    'category': 'Tools/Tools',
    'version': '17.0.0.1',
    
    'depends': ['portal', 'sale', 'account'],

    'data': [
        # 'views/portal_template_views.xml',
        'views/portal_template_view.xml',
        'views/template_views copy.xml',
    ],
    
    #     'assets': {
    #     'portal.assets_frontend': [
    #         'custom_portal/static/src/js/portal_badges.js',
    #     ],
    # },
    
    "license":'AGPL-3',
    "sequence" : -15,
    "application" : True,
    "installable" : True,
    "auto_install" : False,
}
