# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import urllib
import requests

class LpeTiposDocumentos(models.Model):
    _name = 'loc_pe.doctypes'
    _description = 'Tipos de Documentos'

    code = fields.Char(string="Código", required=True)
    name = fields.Char(string="Descripción", required=True)
    sinserie = fields.Boolean("Sin serie")
    register = fields.Selection([
        ('salepurch', 'Registro de Compras y Ventas'),
        ('purch', 'Solo Registro de Compras'),
        ('ret', 'Libro de Retenciones'),
        ('diamay', 'Libro Diario y Mayor'),
    ], string='Registro al que pertenece', readonly=False, default='salepurch')


    _sql_constraints = [
        ('unique_name', 'unique (code)', 'Código duplicado!')
    ]

    def import_csv(self):
        # this will get executed when you click the import button in your form
        print("yes working")
        #resp = requests.get('https://api.bluelytics.com.ar/v2/latest')
        #print(resp.json())

        #myreq = requests.get("https://www.sunat.gob.pe/a/txt/tipoCambio.txt")
        #textdata = myreq.text
        #print(textdata)

        headers = requests.utils.default_headers()
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        r = requests.get('https://www.sunat.gob.pe/a/txt/tipoCambio.txt', headers=headers)
        print(r.text)

        #with open("https://www.sunat.gob.pe/a/txt/tipoCambio.txt") as file:  # Use file to refer to the file object
        #    data = file.read()
        #    print(data)
        return {}


class AccountMove(models.Model):
    _inherit = 'account.move'
    lpe_docType = fields.Many2one('loc_pe.doctypes',string='Tipo de documento', required=True)
