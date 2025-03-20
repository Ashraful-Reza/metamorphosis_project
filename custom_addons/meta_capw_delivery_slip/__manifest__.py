{
    'name': 'Meta CAPW Delivery Slip',
    
    'summary': "This module will help to change the layout of Delivery report.",
    'description': """This module will help to change the layout of Delivery report.""",
    
    'author':"Metamorphosis Ltd, Tanjil",
    'co-author':"Tanjil",
    'website':'https://metamorphosis.com.bd',

    'version': '17.0.0.1',
    'category': 'Tools/Tools',
    'license': 'AGPL-3',
    
    'depends': ['stock'],
    'data': [
        'report/delivery_report_inherit.xml',
    ],

    'sequence':-150,
    "installable": True,
    "application": True,
    'auto_install': False,
}