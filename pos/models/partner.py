# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    membership_code = fields.Char(string='Member name')
    #company_type = fields.Selection(selection_add=[('om', 'Odoo Mates'), ('odoodev', 'Odoo Dev')])
