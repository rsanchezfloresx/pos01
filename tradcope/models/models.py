# -*- coding: utf-8 -*-

from odoo import models, fields, api


class lpeloc(models.Model):
    _name = 'lpeloc.lpeloc'
    _description = 'LPE'

    lpe_sessionId = fields.Integer(string='SessionId', required=False, help='SessionId')
    lpe_rate = fields.Float(string='Rate', required=False, help='Rate')
    lpe_date = fields.Datetime(index=True)
