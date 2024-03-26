# -*- coding: utf-8 -*-


{
    'name': 'employee_screen',
    'description': """employee screen""",
    'version': '1.0',
    'category': 'Hr/Screen',
    'depends': ['base', 'hr', 'hr_payroll', 'add_to_allowance_contracts', 'hr_nevertity'],
    'data': [
        # "security/security.xml",
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/views_penality_group.xml",
        "views/views_penality_sub.xml",
        "views/views_pyslib_inh.xml",

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
