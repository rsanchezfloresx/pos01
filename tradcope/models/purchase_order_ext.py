# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrderExt(models.Model):
    _inherit = "purchase.order"

    lpe_new_rate = fields.Float(string='Nueva tasa monetaria', digits=0,
                        help='Nueva tasa monetaria')

