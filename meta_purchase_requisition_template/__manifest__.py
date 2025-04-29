{
    'name': 'Purchase Requisition Template',
    'summary': 'Purchase Requisition Template',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '18.0.0.1',
    'depends': [
        'purchase',
        'purchase_requisition',
        'meta_purchase_comparison_system'
    ],
    'data': [
        'data/purchase_requisition_data.xml',
        'views/blanket_order.xml',
    ],
    'installable': True,
    'application': True
}