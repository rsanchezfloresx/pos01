# -*- coding: utf-8 -*-

import json
import time
from ast import literal_eval
from collections import defaultdict
from datetime import date
from itertools import groupby
from operator import itemgetter

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, format_datetime
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import format_date

import datetime
from dateutil.relativedelta import relativedelta


class Picking(models.Model):
    _inherit = 'stock.picking'

    # @api.constrains('lpe_new_rate', 'lpe_exc_rate')
    # @api.onchange('lpe_new_rate', 'lpe_exc_rate')
    @api.onchange('lpe_new_rate')
    def check_manual_rate(self):
        for rec in self:
            if rec.lpe_exc_rate == 'manual':
                if rec.lpe_new_rate == 0:
                    raise ValidationError(_('New rate is mandatory'))

    @api.model
    def _get_default_lpe_date_rate(self):
        return fields.Date.context_today(self)

    currency_id = fields.Many2one('res.currency', 'Currency', required=False)

    lpe_exc_rate = fields.Selection([
                  ('sale', 'Venta'),
                  ('purchase', 'Compra'),
                  ('manual', 'Manual'),
        ], string='Tipo de cambio', readonly=False, default='sale')

    lpe_date_rate = fields.Date(
        string='Fecha tasa monetaria',
        required=True,
        index=True,
        readonly=False,
        copy=False,
        default=_get_default_lpe_date_rate
    )

    lpe_rate = fields.Float(compute='_compute_current_rate', string='Tasa monetaria actual', digits=0,
                        help='Tasa monetaria actual')
    lpe_new_rate = fields.Float(string='Nueva tasa monetaria', digits=0,
                        help='Nueva tasa monetaria')

    rate_ids = fields.One2many('res.currency.rate', 'currency_id', string='Rates')

    lpe_dobRate = fields.Boolean(string='Doble tasa')

    def _get_rates(self, company, date, currency):
        res = {}
        self.env['res.currency.rate'].flush(['rate', 'currency_id', 'company_id', 'name'])

        exchrateval = self.lpe_exc_rate
        if exchrateval == 'purchase':
            self._cr.execute("""SELECT lpe_ratec FROM res_currency_rate 
                                WHERE currency_id = %s
                                  AND name <= %s
                                  AND (company_id is null
                                      OR company_id = %s)
                             ORDER BY company_id, name desc LIMIT 1""",
                             (currency, date, company.id))

            if self._cr.rowcount:
                res[1] = self._cr.fetchone()[0]

                if res[1] != 0:
                    res[1] = 1 / res[1]

            else:
                res[1] = 1
                
            lpe_userId = self.env.user.id

            lperatetmp = res[1]

            if exchrateval == 'manual':
                if self.lpe_new_rate != 0:
                    lperatetmp = 1 / self.lpe_new_rate

            self.env.cr.execute('delete from lpeloc_lpeloc where "lpe_sessionId"=%s'%(lpe_userId))
            self.env.cr.execute("""insert into lpeloc_lpeloc (id, "lpe_sessionId", lpe_rate, create_uid, lpe_date) values(%s,%s,%s,%s,%s)""",
                                (lpe_userId, lpe_userId, lperatetmp, lpe_userId, datetime.datetime.now()))


            self._onchange_lpe_exc_rate()
                

        else:
            namestr = isinstance(currency, bool)
            if namestr == False:
                self._cr.execute("""SELECT rate FROM res_currency_rate 
                                    WHERE currency_id = %s
                                      AND name <= %s
                                      AND (company_id is null
                                          OR company_id = %s)
                                 ORDER BY company_id, name desc LIMIT 1""",
                                (currency, date, company.id))

                if self._cr.rowcount:
                    res[1] = self._cr.fetchone()[0]
                else:
                    res[1] = 1


                lpe_userId = self.env.user.id

                lperatetmp = res[1]

                if exchrateval == 'manual':
                    if self.lpe_new_rate != 0:
                        lperatetmp = 1 / self.lpe_new_rate

                self.env.cr.execute('delete from lpeloc_lpeloc where "lpe_sessionId"=%s'%(lpe_userId))
                self.env.cr.execute("""insert into lpeloc_lpeloc (id, "lpe_sessionId", lpe_rate, create_uid, lpe_date) values(%s,%s,%s,%s,%s)""",
                                    (lpe_userId, lpe_userId, lperatetmp, lpe_userId, datetime.datetime.now()))


                self._onchange_lpe_exc_rate()
            else:
                lpe_userId = self.env.user.id
                self.env.cr.execute('delete from lpeloc_lpeloc where "lpe_sessionId"=%s' % (lpe_userId))
                
        return res


    @api.depends('rate_ids.rate', 'lpe_exc_rate', 'lpe_date_rate', 'currency_id', 'lpe_new_rate')
    def _compute_current_rate(self):
        # date = self._context.get('date') or fields.Date.today()
        lpe_borrar = 1
        date_list = self.mapped('lpe_date_rate')
        date = date_list[0]

        date_invoice_list = self.mapped('lpe_date_rate')
        date_invoice = date_invoice_list[0]

        if date_invoice:
            date = date_invoice

        purch = self.purchase_id

        curidrec = purch.mapped('currency_id')
        currency_id = curidrec.id

        exc_rate = self.mapped('lpe_exc_rate')

        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.company
        # the subquery selects the last rate before 'date' for the given currency/company

        currency_rates = self._get_rates(company, date, currency_id)
        for currency in self:
            currency.lpe_rate = currency_rates.get(1) or 1.0

        for record in self:
            record.lpe_dobRate = self.env['res.currency'].search([('id', '=', currency_id)], limit=1).lpe_tasa

        if currency.lpe_rate != 0:
            currency.lpe_rate = 1 / currency.lpe_rate

        return currency.lpe_rate


    # @api.onchange('lpe_exc_rate')
    def _onchange_lpe_exc_rate(self):
        if self.lpe_exc_rate != 'manual':
            self.lpe_new_rate = 0
        # self._onchange_currency()
