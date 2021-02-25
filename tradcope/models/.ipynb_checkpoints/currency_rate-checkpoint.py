# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Currency(models.Model):
    _inherit = 'res.currency'
    lpe_tasa = fields.Boolean(string='Double rate')

    def write(self, vals):
        record = super(Currency, self).write(vals)

        if 'lpe_tasa' in vals:
            self.env.cr.execute('update res_currency_rate set '
                                'lpe_tasa=%s where currency_id=%s',
                                (vals['lpe_tasa'], self.id))
        return record
    
class CurrencyRate(models.Model):
    _inherit = 'res.currency.rate'
    #_sql_constraints = [('unique_name_per_day', 'CHECK(1=1)',
    #                     'This attribute value already exists !')]

    lpe_tasa = fields.Boolean(string='Double rate')
    lpe_ratec = fields.Float(string='Purchase exchange rate', digits=0, default=0.0,
                        help='Purchase exchange rate')
    lpe_ratev = fields.Float(string='Sale exchange rate', digits=0, default=0.0,
                        help='Sale exchange rate')

    #@api.depends('default_currency_id')
    @api.model
    def default_get(self, vals):
        res = super(CurrencyRate, self).default_get(vals)
        parent_id = self._context.get('active_id', False)
        tasa = self.env['res.currency'].search(
            [('id', '=', parent_id)]).lpe_tasa
        if parent_id:
            res.update({
                        'lpe_tasa': tasa
                       })

        return res

    #def _compute_line_tasa(self):
    #    for line in self:
        #    curidrec = line.mapped('currency_id')
        #    tasaval = curidrec.lpe_tasa
    #        curid = line.env.context.get('default_currency_id')
    #        tasaval = line.env['res.currency'].search([('id', '=', curid )]).lpe_tasa

    #        if tasaval:
    #            line.lpe_tasa = tasaval
    #        else:
    #            line.lpe_tasa = False



    #lpe_type = fields.Selection([('compra', 'Compra'),('venta','Venta'),],
    #                          default='compra', string='Tipo')

    #vals.update({'monthly_lines':[(0,0,{'month_name_id':1,'so_qty':35})]})
    @api.model
    def create(self, vals):
        # company_id, currency_id
        amount = 1
        #curidrec = self.mapped('currency_id')
        curid = self.env.context.get('default_currency_id')
        tasaval = self.env['res.currency'].search([('id', '=', curid )]).lpe_tasa

        #for line in self:
        #    curidrec = line.mapped('currency_id')
        #    tasaval = curidrec.lpe_tasa

        if tasaval:
            amount = vals['lpe_ratev']

            if amount <= 0:
                amount = 1
            else:
                amount = 1 / amount

            vals['rate'] = amount
        res = super(CurrencyRate, self).create(vals)

        return res

    def write(self, vals):
        #company_id, currency_id
        amount = 0

        #mini_rec = self.env['est.weight'].search([])

        curidrec = self.mapped('currency_id')
        #comidrec = self.mapped('company_id')

        #curid = 2
        tasaval = curidrec.lpe_tasa


        #tasaid = (self.env["res.currency"].search([("id", "=", curid)])).lpe_tasa




        #'lpe_tasa' in vals.keys():
        #if self.lpe_tasa:
        #tasaval = self.lpe_tasa
        #vals['lpe_tasa']

        if tasaval:
            amount = vals['lpe_ratev']
            #vals['lpe_ratev']

            if amount <= 0:
                amount = 0
            else:
                amount = 1 / amount

            vals.update({'rate': amount})
            #self.rate = amount
            #self.write({'rate': False})

        record = super(CurrencyRate, self).write(vals)

        return record