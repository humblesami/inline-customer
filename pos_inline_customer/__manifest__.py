# -*- coding: utf-8 -*-
{
    'name': "Pos Inline Customer",
    'description': """
        Customer Selection Brought to Order Page
    """,

    'author': "sami",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        'views/inline_customer.xml'
    ],
    'qweb': [
        'static/inline_customer.xml',
    ],
    'application': True
}
