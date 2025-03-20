# -*- coding: utf-8 -*-
# from odoo import http


# class MetaBomTransferProcess(http.Controller):
#     @http.route('/meta_bom_transfer_process/meta_bom_transfer_process', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/meta_bom_transfer_process/meta_bom_transfer_process/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('meta_bom_transfer_process.listing', {
#             'root': '/meta_bom_transfer_process/meta_bom_transfer_process',
#             'objects': http.request.env['meta_bom_transfer_process.meta_bom_transfer_process'].search([]),
#         })

#     @http.route('/meta_bom_transfer_process/meta_bom_transfer_process/objects/<model("meta_bom_transfer_process.meta_bom_transfer_process"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('meta_bom_transfer_process.object', {
#             'object': obj
#         })

