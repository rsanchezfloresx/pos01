# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class WebsiteContact(http.Controller):

    @http.route(['/customers'], type='http', auth="user", website=True)
    def customer(self):
        #customers = request.env['res.partner'].search([])
        customers = request.env['res.partner'].search([('company_type', '=', 'company')])
        values = {
            'customers': customers,
        }
        return request.render('pos.customer', values)

    @http.route(['/customers/details/<model("res.partner"):customer>'], type='http', auth="public", website=True)
    def customer_details(self, customer):
        values = {'customer':customer}
        return request.render("pos.customer_details", values)
