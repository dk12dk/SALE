##############################################################################
#
#   Standard Transaction Module
#
##############################################################################

{
    'name': 'Kite Sale Order',
    'version': '0.1',
    'author': 'admin',
    'depends' : ['base','product'],
    'data': [
		'kite_sale_order_view.xml',
		],
    'css': ['static/src/css/state.css'], 		
    'auto_install': False,
    'installable': True,
}

