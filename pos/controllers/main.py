# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression
_logger = logging.getLogger(__name__)

from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteShop(WebsiteSale):

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        """  override the function to rewrite the auth to user from public """
        res = super(WebsiteShop, self).shop(page=page, category=category, search=search, ppg=ppg, **post)
        return res
    '''
    @http.route(['/shop/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=True)
    def product(self, product, category='', search='', **kwargs):

        # if not product.can_access_from_current_website():
        #    raise NotFound()

        # return request.render("website_sale.product", self._prepare_product_values(product, category, search, **kwargs))


       product_context = dict(request.env.context, active_id=product.id)
       ProductCategory = request.env['product.public.category']
       Rating = request.env['rating.rating'].sudo()
       if category:
           category = ProductCategory.browse(int(category)).exists()
       attrib_list = request.httprequest.args.getlist('attrib')
       attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
       attrib_set = set([v[1] for v in attrib_values])
       keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)
       categs = ProductCategory.search([('parent_id', '=', False)])
       pricelist = request.website.get_current_pricelist()
       from_currency = request.env.user.company_id.currency_id
       to_currency = pricelist.currency_id
       compute_currency = lambda price: from_currency.compute(price, to_currency)
       # get the rating attached to a mail.message, and the rating stats of the product
       ratings = Rating.search([('message_id', 'in', product.website_message_ids.ids)])
       rating_message_values = dict([(record.message_id.id, record.rating) for record in ratings])
       if not product_context.get('pricelist'):
           product_context['pricelist'] = pricelist.id
           product = product.with_context(product_context)
       customer_countries = []
       sale_obj = request.env['sale.order'].search([]).sudo()
       country_vals = []
       for order in sale_obj:
           country_vals.append({order.partner_id.country_id.name})
       for country in country_vals:
           if country not in customer_countries:
               customer_countries.append(country)
       values = {
           'search': search,
           'category': category,
           'pricelist': pricelist,
           'attrib_values': attrib_values,
           'compute_currency': compute_currency,
           'attrib_set': attrib_set,
           'keep': keep,
           'categories': categs,
           'main_object': product,
           'product': product,
           'customer_countries': customer_countries
       }
       return request.render("website_sale.product", values)
    '''
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else: # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                            (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                # TDE FIXME: don't ever do this
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id

        type_rec = request.env['l10n_latam.identification.type'].sudo().search(['|', '|', ('name', '=', 'VAT'), ('name', '=', 'Pasaporte'), ('name', '=', 'Cédula Extranjera')])

        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'country_states': country.get_website_sale_states(mode=mode[1]),
            'countries': country.get_website_sale_countries(mode=mode[1]),
            'type_rec': type_rec,
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }

        return request.render("website_sale.address", render_values)
