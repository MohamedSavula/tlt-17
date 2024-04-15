# -*- coding: utf-8 -*-
{
    'name': "field_in_purchase_agreements",

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
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase', 'purchase_requisition', 'purchase_requisition_stock',
                'edit_purchase_order', 'purchase_agreements_template'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/print_purchase_agreement.xml',
    ],
    'license': 'LGPL-3',
}
