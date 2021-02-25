# -*- coding: utf-8 -*-
{
    'name': "lpeloc14",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.3',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','stock','account','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizard/account_payment_register_ext.xml',
        'views/currency.xml',
        'views/account_payment_ext.xml',
        'views/account_move_ext.xml',
        'views/stock_picking_ext.xml',
        'views/product_pricelist_ext.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
