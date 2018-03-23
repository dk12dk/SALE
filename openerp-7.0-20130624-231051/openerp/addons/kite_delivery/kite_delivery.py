from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import datetime
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')


class kite_delivery(osv.osv):
	
	_name = "kite.delivery"
	_order = "name desc"

	_columns = {
	
				
		'remark': fields.text('Remarks'),
		
		'user_id': fields.many2one('res.users', 'Created By', readonly=True),
		'crt_date':fields.datetime('Created Date',readonly=True),
		'company_id': fields.many2one('res.company', 'Company Name',readonly=True),	
		'name': fields.char('Delivery No', required=True),
		'so_date': fields.datetime('Delivery Date', required=True),
		'state': fields.selection([('draft','Draft'),('confirm','Confirmed')],'Status', readonly=True),

		'customer_id': fields.many2one('res.partner', 'Customer Name', required=True),
		'cus_address': fields.text('Address'),
		'cus_po': fields.char('Customer PO No'),
		'cus_ref': fields.char('Customer Reference'),
		'cus_po_date': fields.datetime('Customer PO Date', readonly=True),
		'mode_of_delivery':fields.selection([('by_air','By Air'),('by_road','By Road'),('by_sea','By Sea')],'Mode of Delivey ',readonly=True),

		'line_ids':fields.one2many('kite.delivery.line', 'header_id', 'Line Details'),
		
		'so_nos':fields.many2many('kite.sale.order.line','multiple_saleorder','schedule_id','so_id','Sale Order',domain="[('customer_id','=',customer_id),('pending_qty','>','0')]"),



	}
	
	_defaults = {
			
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kite_delivery', context=c),			
		'crt_date' : lambda * a: time.strftime('%Y-%m-%d'),
		'user_id': lambda obj, cr, uid, context: uid,
		'state': 'draft',		
	}	
	

	def update_so(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		sql = """delete from kite_delivery_line where header_id= %s"""%(ids[0])		
		cr.execute(sql)	
		line_obj = self.pool.get("kite.delivery.line")
		if rec.so_nos:
			for val in rec.so_nos:
				if val.pending_qty > 0:
					line_obj.create(cr, uid, {
								'header_id':rec.id,
								'sale_line':val.id,
								'product_id':val.product_id.id,
								'unit_price':val.unit_price,
								'order_qty':val.order_qty,
								'delivery_date':val.delivery_date,
								'cus_price':val.cus_price,
								'pending_qty':val.pending_qty,
							})
				self.write(cr, uid, ids, {'cus_address':val.header_id.cus_address,'cus_ref':val.header_id.cus_ref,'mode_of_delivery':val.header_id.mode_of_delivery,'cus_po_date':val.header_id.cus_po_date,'cus_po':val.header_id.cus_po})	
		return True


	def entry_confirm(self, cr, uid, ids,context=None):
		obj_rec = self.browse(cr, uid, ids[0])
		sale_line_obj = self.pool.get("kite.sale.order.line")
		for val in obj_rec.line_ids:
			if val.order_qty ==0:
				raise osv.except_osv(_('Warning!'),
				_('You cannot allowed to confirm with 0 order qty for product %s')%(val.product_id.name_template))
			val.write({'pending_qty':val.order_qty})
			remain_qty =((val.sale_line.pending_qty - val.order_qty))
			if remain_qty >0:
				remain_qty =remain_qty
			else:
				remain_qty =0		

			sale_line_obj.write(cr, uid,val.sale_line.id, {'pending_qty': remain_qty})	
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
		return super(kite_delivery, self).create(cr, uid, vals, context=context)
		
	def write(self, cr, uid, ids, vals, context=None):
		return super(kite_delivery, self).write(cr, uid, ids, vals, context)		
	
	
	
kite_delivery()

class kite_delivery_line(osv.osv):
	
	_name = "kite.delivery.line"


	_columns = {
	
	
		'header_id':fields.many2one('kite.delivery', 'Delivery No', required=1, ondelete='cascade'),
		'remark': fields.text('Remarks'),
		
		'name': fields.related('header_id','name',type='char', string='Delivery No'),
		'customer_id': fields.related('header_id','customer_id', type='many2one',relation='res.partner', string='Customer Name', store=True),
		'delivery_date': fields.date('Delivery Date', required=True),
		'order_qty': fields.float('Order Qty',required=True),
		'unit_price': fields.float('Unit Price',required=True),
		'pending_qty': fields.float('Pending Qty'),
		'cus_price': fields.float('Customer PO Unit Price',required=True),
		
		
		'product_id':fields.many2one('product.product','Item Name',required=True),		
		'sale_line':fields.many2one('kite.sale.order.line','Sale Line Id'),		
		
		
		
		}




	
kite_delivery_line()

