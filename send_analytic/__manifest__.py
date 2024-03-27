# -*- coding: utf-8 -*-
{
    'name': "send_analytic",
    'summary': """send analytic from stock picking to journal entries""",
    'description': """send analytic from stock picking to journal entries""",
    'author': "M.Saber",
    'category': 'stock',
    'version': '0.1',
    'depends': ['base', 'stock', 'stock_account', 'analytic', 'account', 'sale'],
    'data': [
        'views/views.xml',
    ],
    'license': 'LGPL-3',
}
