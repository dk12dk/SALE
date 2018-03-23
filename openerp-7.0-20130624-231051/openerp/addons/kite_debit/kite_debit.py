from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import datetime
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')


class kite_debit(osv.osv):
	
	_name = "kite.debit"
	_order = "name desc"
	
	
	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		for order in self.browse(cr, uid, ids, context=context):
			res[order.id] = {
				'total': 0.0,
			}
			val1 =0
			val1 += order.product_qty * order.unit_price 
			res[order.id]['total']=(round(val1))
		return res
	

	_columns = {
	
				
		'remark': fields.text('Remarks'),
		
		'user_id': fields.many2one('res.users', 'Created By', readonly=True),
		'crt_date':fields.datetime('Created Date',readonly=True),
		'company_id': fields.many2one('res.company', 'Company Name',readonly=True),	
		'name': fields.char('Debit No', required=True),
		'entry_date': fields.datetime('Debit Date', required=True),
		'state': fields.selection([('draft','Draft'),('confirm','Confirmed')],'Status', readonly=True),
		'product_qty': fields.float('Product Qty', required=True),
		'pending_qty': fields.float('Pending Qty' ),
		'unit_price': fields.float('Unit Price', required=True),
		'total': fields.function(_amount_all, string='Total',store=True,multi="sums",help="The total amount"),
		'product_id': fields.many2one('product.product', 'Product Name',required=True),	
		'sale_id': fields.many2one('kite.sale.order', 'SO No',required=True),	
		'customer_id': fields.many2one('res.partner', 'Customer Name',required=True),	

		



	}
	
	_defaults = {
			
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kite_debit', context=c),			
		'crt_date' : lambda * a: time.strftime('%Y-%m-%d'),
		'user_id': lambda obj, cr, uid, context: uid,
		'state': 'draft',		
	}	
	

	


	def entry_confirm(self, cr, uid, ids,context=None):
		obj_rec = self.browse(cr, uid, ids[0])
		if obj_rec.product_qty ==0:
			raise osv.except_osv(_('Warning!'),
			_('You cannot allowed to confirm with 0 Product qty'))			
		self.write(cr,uid,ids[0],{'state':'confirm' ,'pending_qty':obj_rec.product_qty })								  
		return True

	
		
	def unlink(self,cr,uid,ids,context=None):
		unlink_ids = []		
		for rec in self.browse(cr,uid,ids):	
			if rec.state != 'draft':			
				raise osv.except_osv(_('Warning!'),
						_('You can not delete this entry !!'))
			else:
				unlink_ids.append(rec.id)
		return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		
	def create(self, cr, uid, vals, context=None):
		return super(kite_debit, self).create(cr, uid, vals, context=context)
		
	def write(self, cr, uid, ids, vals, context=None):
		return super(kite_debit, self).write(cr, uid, ids, vals, context)		
	
	
	
kite_debit()

