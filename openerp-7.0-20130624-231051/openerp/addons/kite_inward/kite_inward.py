from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import datetime
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')


class kite_inward(osv.osv):
	
	_name = "kite.inward"
	_order = "name desc"

	_columns = {
	
				
		'remark': fields.text('Remarks'),
		
		'user_id': fields.many2one('res.users', 'Created By', readonly=True),
		'crt_date':fields.datetime('Created Date',readonly=True),
		'company_id': fields.many2one('res.company', 'Company Name',readonly=True),	
		'name': fields.char('Inward No', required=True),
		'entry_date': fields.datetime('Inward Date', required=True),
		'state': fields.selection([('draft','Draft'),('confirm','Confirmed')],'Status', readonly=True),
		'stock_qty': fields.float('Stock Qty', required=True),
		'pending_qty': fields.float('Pending Qty'),
		'product_id': fields.many2one('product.product', 'Product Name',required=True),	

		



	}
	
	_defaults = {
			
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kite_inward', context=c),			
		'crt_date' : lambda * a: time.strftime('%Y-%m-%d'),
		'user_id': lambda obj, cr, uid, context: uid,
		'state': 'draft',		
	}	
	

	


	def entry_confirm(self, cr, uid, ids,context=None):
		obj_rec = self.browse(cr, uid, ids[0])
		if obj_rec.stock_qty ==0:
			raise osv.except_osv(_('Warning!'),
			_('You cannot allowed to confirm with 0 Product qty'))			
		self.write(cr,uid,ids[0],{'state':'confirm' ,'pending_qty':obj_rec.stock_qty })								  
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
		return super(kite_inward, self).create(cr, uid, vals, context=context)
		
	def write(self, cr, uid, ids, vals, context=None):
		return super(kite_inward, self).write(cr, uid, ids, vals, context)		
	
	
	
kite_inward()

