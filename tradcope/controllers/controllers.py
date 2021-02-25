# -*- coding: utf-8 -*-
# from odoo import http


# class LocMonedas(http.Controller):
#     @http.route('/loc_monedas/loc_monedas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/loc_monedas/loc_monedas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('loc_monedas.listing', {
#             'root': '/loc_monedas/loc_monedas',
#             'objects': http.request.env['loc_monedas.loc_monedas'].search([]),
#         })

#     @http.route('/loc_monedas/loc_monedas/objects/<model("loc_monedas.loc_monedas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('loc_monedas.object', {
#             'object': obj
#         })
