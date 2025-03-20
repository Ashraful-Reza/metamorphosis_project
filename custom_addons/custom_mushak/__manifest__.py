{
    'name': 'Custom Mushak Reports',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Bangladesh Tax Reports (Mushak 6.6)',
    'description': """
        This module adds Bangladesh Tax Reports (Mushak) to invoices.
        Features:
        - Adds BIN ID field to partner records
        - Adds Mushak 6.6 report to invoices
    """,
    'author': 'Metamorphosis Ltd',
    'co-author': 'Tanjil',
    'website': 'https://metamorphosis.com.bd',
    'depends': [
        'account',
        'web',
    ],
    'data': [
        'views/res_partner_views.xml',
        'reports/mushak_report.xml',
        'views/account_move_views.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'custom_mushak/static/description/nbr_logo.png',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
















# {
#     'name': 'Mushak Invoice Report',
#     'version': '1.0',
#     'author':'Metamorphosis Ltd., AR Tanjil ',
#     'category': 'Accounting',
#     "description": "Adds Mushak print report to invoices",
#     'depends': ['base','account'],
#     'data': [
#         # 'security/ir.model.access.csv',
#         #'views/respartner.xml',
#         'views/account_move_views.xml',
#         # 'report/custom_invoice_report.xml',
#         # 'report/invoice_report.xml',
#         # 'views/account_move_views.xml',
#         "report/mushak_invoice_report.xml",
#         "reports/mushak_invoice_template.xml"
#     ],
#     'assets': {
#         'web.report_assets_common': [
#             'custom_mushak/static/description/nbr_logo.png',
#         ],},
#     "installable": True,
#     "application": True,
#     'auto_install':False,
# }