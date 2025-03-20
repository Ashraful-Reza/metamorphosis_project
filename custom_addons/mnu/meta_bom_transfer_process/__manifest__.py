# -*- coding: utf-8 -*-
{
    'name': "Bom Transfer Process",

    'summary': "This will select all the component of the the bom selected in the stock picking or the transfer to avoid the hestle of select bom component for the move.",

    'description': """This will select all the component of the the bom selected in the stock picking or the transfer to avoid the hestle of select bom component for the move.""",

    'author': "Metamorphosis LTD, Rifat Anwar",
    'co-author': "Rifat Anwar",
    'website': "https://metamorphosis.com.bd",
    'category': 'Tools/Tools',
    'version': '17.0.0.1',

    'depends': ['base','stock','mrp','sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/stock_pick_view.xml',
        'views/mrp_production_view.xml',
        'wizard/production_bom_wiz_view.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'meta_bom_transfer_process/static/src/**/*.js',
    #         'meta_bom_transfer_process/static/src/**/*.xml',
    #     ],
    # },
    'sequence':-100,
    'license':'AGPL-3',
    'installable':True,
    'auto-installable':False,
    'application':True,
}

