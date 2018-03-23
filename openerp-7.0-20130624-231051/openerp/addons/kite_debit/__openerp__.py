##############################################################################
#
#   Standard Transaction Module
#
##############################################################################

{
    'name': 'Kite Debit Note',
    'version': '0.1',
    'author': 'admin',
    'depends' : ['base','product','kite_sale_order'],
    'data': [
		'kite_debit_view.xml',
		],
    'css': ['static/src/css/state.css'], 		
    'auto_install': False,
    'installable': True,
}

