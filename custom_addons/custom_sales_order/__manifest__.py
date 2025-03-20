{
    'name': 'Custom Sales Order ',
    
    'summary': "This module will help to create sales order",
    'description': """This module will help to change normal view to wizard view .""",
    
    'author':"Metamorphosis Ltd, Tanjil",
    'co-author':"Tanjil",
    'website':'https://metamorphosis.com.bd',

    'version': '17.0.0.1',
    'category': 'Tools/Tools',
    'license': 'AGPL-3',
    
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_discount_approval_views.xml',
        'views/sale_order_views.xml',
    ],

    'sequence':-250,
    "installable": True,
    "application": True,
    'auto_install': False,
}