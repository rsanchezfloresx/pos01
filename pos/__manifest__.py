# -*- coding: utf-8 -*-
{
    'name': "POS PERU",

    'summary': """
        POS
        PERU""",
    'sequence': 30,
    'description': """
        POS PERU
    """,

    'author': "TPCG",
    'website': "http://www.tpcg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'LocPeru',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'point_of_sale',
                'l10n_pe',
                'website_sale'],

    # always loaded
    'data': [
            'data/menu.xml',
            # 'views/customer_template.xml',
            # 'views/customer_tpage_template.xml',
            'views/search.xml',
            'views/customer_tsearch_template.xml',
            # 'views/customer_ucategory_template.xml',
            'views/pos_assets_template.xml',
            'views/partner_view.xml',
            'views/website_sale_templates.xml',
    ],
    'qweb': [
            'static/src/xml/Screens/ReceiptScreen/OrderReceipt.xml',
            'static/src/xml/Screens/ClientListScreen/ClientDetailsEdit.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}