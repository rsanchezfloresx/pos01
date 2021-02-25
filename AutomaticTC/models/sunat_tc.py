# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
import urllib
import requests

class LpeSunatTc(models.Model):
    _name = 'lpesunat.tc'
    _description = 'TC Sunat'

    @api.model
    def run_cron_job(self):
        print("Job RSF")
        headers = requests.utils.default_headers()
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        r = requests.get('https://www.sunat.gob.pe/a/txt/tipoCambio.txt', headers=headers)

        cadenaUrl = r.text
        vfecha = cadenaUrl.split("|")[0]
        vCompra = cadenaUrl.split("|")[1]
        vVenta = cadenaUrl.split("|")[2]

        if vfecha:
            date_value = self.env['lpesunat.tc'].search([('fecha', '=', vfecha)]).fecha
            found = False

            if date_value:
                found = True
            else:
                attach_vals = {'fecha': vfecha, 'compra': vCompra, 'venta': vVenta}
                self.env['lpesunat.tc'].create(attach_vals)

                fechaTC = datetime.strptime(vfecha, '%d/%m/%Y')
                fechaTCDate = fechaTC.date()

                date_value = self.env['res.currency.rate'].search([('currency_id', '=', 2),('name', '=', fechaTCDate)]).name

                if date_value:
                    found = True
                else:
                    found = False
                    vCompany = self.env.user.company_id.id
                    vCompraNum = float(vCompra)
                    vVentaNum = float(vVenta)

                    vVentaNum = vVentaNum

                    if vVentaNum != 0:
                        vRate = 1 / vVentaNum

                    attach_vals = {'name': fechaTCDate, 'currency_id': 2, 'company_id': vCompany, 'rate': vRate, 'lpe_tasa': True, 'lpe_ratec': vCompraNum, 'lpe_ratev': vVentaNum}
                    self.env['res.currency.rate'].create(attach_vals)




    fecha = fields.Char(string='Fecha')
    compra = fields.Char(string='Compra')
    venta = fields.Char(string='Venta')
    #compra = fields.Float(string='Compra', digits=(12, 6))
    #venta = fields.Float(string='Venta', digits=(12, 6))