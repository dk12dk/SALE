from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import datetime
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')


class kite_sale_order(osv.osv):
	
	_name = "kite.sale.order"
	_order = "name desc"

	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		for order in self.browse(cr, uid, ids, context=context):
			res[order.id] = {
				'amount_total': 0.0,
			}
			val1 =0
			for line in order.line_ids:
				val1 += line.order_qty * line.unit_price 
			res[order.id]['amount_total']=(round(val1))
		return res

	
	_columns = {
	
				
		'remark': fields.text('Remarks'),
		
		'user_id': fields.many2one('res.users', 'Created By', readonly=True),
		'crt_date':fields.datetime('Created Date',readonly=True),
		'company_id': fields.many2one('res.company', 'Company Name',readonly=True),	
		'name': fields.char('SO No', required=True),
		'so_date': fields.datetime('SO Date', required=True),
		'state': fields.selection([('draft','Draft'),('confirm','Confirmed')],'Status', readonly=True),

		'customer_id': fields.many2one('res.partner', 'Customer Name', required=True),
		'amount_total': fields.function(_amount_all, string='Total',store=True,multi="sums",help="The total amount"),
		'cus_address': fields.text('Address'),
		'cus_po': fields.char('Customer PO No'),
		'cus_ref': fields.char('Customer Reference'),
		'cus_po_date': fields.datetime('Customer PO Date', required=True),
		'mode_of_delivery':fields.selection([('by_air','By Air'),('by_road','By Road'),('by_sea','By Sea')],'Mode of Delivey ',required=True),

		'line_ids':fields.one2many('kite.sale.order.line', 'header_id', 'Line Details'),



	}
	
	_defaults = {
			
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kite_sale_order', context=c),			
		'crt_date' : lambda * a: time.strftime('%Y-%m-%d'),
		'user_id': lambda obj, cr, uid, context: uid,
		'state': 'draft',		
	}	
	
	def onchange_cus_id(self,cr,uid,ids,customer_id,context = None):
		print "customer_idcustomer_idcustomer_idcustomer_id",customer_id
		cus_obj = self.pool.get("res.partner")
		cus_rec = cus_obj.browse(cr,uid,customer_id)
		print "cus_rec.streetcus_rec.streetcus_rec.street",cus_rec.name
		tot_add = (cus_rec.street or '')+ ' ' + (cus_rec.street2 or '') + '\n'+(cus_rec.city or '')+ ',' +(cus_rec.state_id.name or '') + '-' +(cus_rec.zip or '') + '\nPh:' + (cus_rec.phone or '')+ '\n' +(cus_rec.mobile or '')		
		return {'value':{'cus_address':tot_add}}

	def entry_confirm(self, cr, uid, ids,context=None):
		obj_rec = self.browse(cr, uid, ids[0])
		for val in obj_rec.line_ids:
			if val.order_qty ==0:
				raise osv.except_osv(_('Warning!'),
				_('You cannot allowed to confirm with 0 order qty for product %s')%(val.product_id.name_template))
			if val.unit_price ==0:
				raise osv.except_osv(_('Warning!'),
				_('You cannot allowed to confirm with 0 Unit Price for product %s')%(val.product_id.name_template))
			val.write({'pending_qty':val.order_qty,'inv_pending_qty':val.order_qty})
		self.write(cr,uid,ids[0],{'state':'confirm' })								  
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
		return super(kite_sale_order, self).create(cr, uid, vals, context=context)
		
	def write(self, cr, uid, ids, vals, context=None):
		vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),'update_user_id':uid})
		return super(kite_sale_order, self).write(cr, uid, ids, vals, context)		
	
	
	
kite_sale_order()

class kite_sale_order_line(osv.osv):
	
	_name = "kite.sale.order.line"


	_columns = {
	
	
		'header_id':fields.many2one('kite.sale.order', 'so No', required=1, ondelete='cascade'),
		'remark': fields.text('Remarks'),
		
		'name': fields.related('header_id','name',type='char', string='SO No'),
		#~ 'customer_id': fields.related('header_id','customer_id',type='many2one', string='Customer'),
		'customer_id': fields.related('header_id','customer_id', type='many2one',relation='res.partner', string='Customer Name', store=True),
		'delivery_date': fields.date('Delivery Date', required=True),
		'order_qty': fields.float('Order Qty',required=True),
		'unit_price': fields.float('Unit Price',required=True),
		'sub_total': fields.float('Sub Total',readonly=True),
		'pending_qty': fields.float('Pending Qty'),
		'inv_pending_qty': fields.float('Inv Pending Qty'),
		'cus_price': fields.float('Customer PO Unit Price',required=True),
		
		
		'product_id':fields.many2one('product.product','Item Name',required=True),		
		
		
		
		}




	
kite_sale_order_line()

