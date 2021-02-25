# -*- coding: utf-8 -*-
{
    'name': "T/C automático SUNAT",

    'summary': """
        T/C automático - SUNAT
        PERU""",

    'description': """
        T/C automático SUNAT
    """,

    'author': "TPCG",
    'website': "http://www.tpcg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'LocPeru',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'data/cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}