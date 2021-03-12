# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class WebsiteContact(http.Controller):

    @http.route(
        ['/customers', '/customers/page/<int:page>', '/customers/category/<model("res.partner.category"):category>'],
        type='http', auth="user", website=True)
    def customer(self, page=0, search='', category=None):
        domain = []

        # for Search option
        if search:
            domain = [('name', 'ilike', search)]

        total_customers = request.env['res.partner'].search(domain)
        total_count = len(total_customers)
        per_page = 12

        # total : Total count of records
        # page  : Current Page
        # step  : Count of records need to display in one page
        # scope : Count of pages needs to display in pager at a time

        pager = request.website.pager(url='/customers', total=total_count, page=page, step=per_page, scope=3,
                                      url_args=None)
        # offset = Count to exclude (first n)

        customers = request.env['res.partner'].search(domain, limit=per_page, offset=pager['offset'], order='id asc')
        if category:
            customers = customers.filtered(lambda rec: category.id in rec.category_id.ids)

        groups = request.env['res.partner.category'].search([])

        if not category:
            category = request.env['res.partner.category']

        values = {
            'customers': customers,
            'pager': pager,
            'groups': groups,
            'category': category,
        }
        return request.render('pos.customer', values)

    @http.route(['/customers/details/<model("res.partner"):customer>'], type='http', auth="public", website=True)
    def customer_details(self, customer):
        values = {'customer':customer}
        return request.render("pos.customer_details", values)
