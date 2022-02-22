# -*- coding: utf-8 -*-
{
    'name': "Customized Base",

    'summary': """
        pos Base app for minor customization in views for ease of use
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "sami",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    'application':True,
}
