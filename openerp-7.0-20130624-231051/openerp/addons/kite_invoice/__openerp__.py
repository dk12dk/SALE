##############################################################################
#
#   Standard Transaction Module
#
##############################################################################

{
    'name': 'Kite Invoice',
    'version': '0.1',
    'author': 'admin',
    'depends' : ['base','product','kite_sale_order','kite_debit'],
    'data': [
		'kite_invoice_view.xml',
		],
    'css': ['static/src/css/state.css'], 		
    'auto_install': False,
    'installable': True,
}

