# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import datetime
from dateutil.relativedelta import relativedelta


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

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

        else:
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

        #query = """SELECT c.id,
        #                  COALESCE((SELECT r.rate FROM res_currency_rate r
        #                          WHERE r.currency_id = c.id AND r.name <= %s
        #                            AND (r.company_id IS NULL OR r.company_id = %s)
        #                       ORDER BY r.company_id, r.name DESC
        #                          LIMIT 1), 1.0) AS rate
        #           FROM res_currency c
        #           WHERE c.id IN %s"""
        #self._cr.execute(query, (date, company.id, tuple(self.ids)))
        #currency_rates = dict(self._cr.fetchall())

        lpe_userId = self.env.user.id

        lperatetmp = res[1]

        if exchrateval == 'manual':
            if self.lpe_new_rate != 0:
                lperatetmp = 1 / self.lpe_new_rate

        self.env.cr.execute('delete from lpeloc_lpeloc where "lpe_sessionId"=%s'%(lpe_userId))
        '''
        self.env.cr.execute('update lpeloc_lpeloc set '
                            'lpe_rate=%s where "lpe_sessionId"=%s',
                            (res[1], lpe_userId))
        '''
        '''
        self.env.cr.execute('insert into lpeloc_lpeloc values(%s,%s,%s,%s)',
                            (lpe_userId, lpe_userId, lperatetmp, lpe_userId))
        '''
        self.env.cr.execute("""insert into lpeloc_lpeloc (id, "lpe_sessionId", lpe_rate, create_uid, lpe_date) values(%s,%s,%s,%s,%s)""",
                            (lpe_userId, lpe_userId, lperatetmp, lpe_userId, datetime.datetime.now()))

        self._onchange_lpe_exc_rate()
        return res

    @api.depends('rate_ids.rate', 'lpe_exc_rate', 'lpe_date_rate', 'currency_id', 'lpe_new_rate')
    def _compute_current_rate(self):
        # date = self._context.get('date') or fields.Date.today()
        date_list = self.mapped('payment_date')
        date = date_list[0]

        date_invoice_list = self.mapped('lpe_date_rate')
        date_invoice = date_invoice_list[0]

        if date_invoice:
            date = date_invoice

        curidrec = self.mapped('currency_id')
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

    # @api.onchange('lpe_rate')
    def _onchange_lpe_exc_rate(self):
        if self.lpe_exc_rate != 'manual':
            self.lpe_new_rate = 0
        # self._onchange_currency()

    #LPE
    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_id': self.payment_method_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'lpe_date_rate': self.lpe_date_rate,
            'lpe_exc_rate': self.lpe_exc_rate,
            'lpe_rate': self.lpe_rate,
            'lpe_new_rate': self.lpe_new_rate,
            'lpe_dobRate': self.lpe_dobRate
        }

        if self.payment_difference and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals
