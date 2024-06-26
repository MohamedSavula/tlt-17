# -*- coding: utf-8 -*-
{
    'name': "edit_in_hr_employe",

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
    'depends': ['base', 'hr', 'hr_contract', 'loans_and_addvance', 'hr_holidays'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/outlet.xml',
        'views/sequance.xml',
        'views/allowances.xml',
        'views/contract.xml',
        'views/deduction.xml',
        'views/transportation_elgonna.xml',
        'views/time_of.xml',
    ],
    'license': 'LGPL-3',
}
