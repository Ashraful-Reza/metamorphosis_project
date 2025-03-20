# -*- coding: utf-8 -*-
{
    'name': "Meta Chatter Bottom",

    'summary': "This module changes the position of the chatter",

    'description': """Chatter bottom position""",

    'author': "metamorphosis",
    'website': "https://www.Metamorphosis.com",
    'category': 'Tools/Tools',
	'licence':'AGPL-3',
    'version': '17.0.0.1',

    'depends': ['base','sale'],

    'data': [
        # 'security/ir.model.access.csv',
    ],
	
    'assets':{
		'web.assets_backend':[
			'/meta_chatter_bottom/static/src/css/style.css',
        ]
    },
	
    'sequence':1,
	'installable':True,
	'application':True
}