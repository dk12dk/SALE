from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import datetime
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')


class kite_invoice(osv.osv):
	
	_name = "kite.invoice"
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
		'name': fields.char('Invoice No', required=True),
		'so_date': fields.datetime('Invoice Date', required=True),
		'state': fields.selection([('draft','Draft'),('confirm','Confirmed')],'Status', readonly=True),

		'customer_id': fields.many2one('res.partner', 'Customer Name', required=True),
		'amount_total': fields.function(_amount_all, string='Total',store=True,multi="sums",help="The total amount"),
		'cus_address': fields.text('Address'),
		'cus_po': fields.char('Customer PO No'),
		'cus_ref': fields.char('Customer Reference'),
		'cus_po_date': fields.datetime('Customer PO Date'),

		'line_ids':fields.one2many('kite.invoice.line', 'header_id', 'Line Details'),
		'line_ids_debit':fields.one2many('kite.invoice.debit', 'header_id', 'Debit Details'),
	
		'so_nos':fields.many2many('kite.sale.order.line','multiple_saleorder_invoice','schedule_id','so_id','Sale Order',domain="[('customer_id','=',customer_id),('inv_pending_qty','>','0')]"),



	}
	
	_defaults = {
			
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kite_invoice', context=c),			
		'crt_date' : lambda * a: time.strftime('%Y-%m-%d'),
		'user_id': lambda obj, cr, uid, context: uid,
		'state': 'draft',		
	}	



	def update_so(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		sql = """delete from kite_invoice_line where header_id= %s"""%(ids[0])		
		cr.execute(sql)	
		line_obj = self.pool.get("kite.invoice.line")
		if rec.so_nos:
			for val in rec.so_nos:
				if val.inv_pending_qty > 0:
					line_obj.create(cr, uid, {
								'header_id':rec.id,
								'sale_line':val.id,
								'product_id':val.product_id.id,
								'unit_price':val.unit_price,
								'order_qty':val.order_qty,
								'delivery_date':val.delivery_date,
								'cus_price':val.cus_price,
								'pending_qty':val.inv_pending_qty,
							})
				self.write(cr, uid, ids, {'cus_address':val.header_id.cus_address,'cus_ref':val.header_id.cus_ref,'cus_po_date':val.header_id.cus_po_date,'cus_po':val.header_id.cus_po})	
		return True

	def update_debit(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		sql = """delete from kite_invoice_debit where header_id= %s"""%(ids[0])		
		cr.execute(sql)	
		line_obj = self.pool.get("kite.invoice.debit")
		cr.execute(""" select * from kite_debit where customer_id = %s and pending_qty >0 """ %(rec.customer_id.id))		
		data3 = cr.dictfetchall()
		if data3:
			for val in data3:
				line_obj.create(cr, uid, {
							'header_id':rec.id,
							'debit_id':val['id'],
							'product_id':val['product_id'],
							'unit_price':val['unit_price'],
							'order_qty':val['product_qty'],
							'sub_total':val['product_qty'] * val['unit_price'],
						})
		return True

	
	def onchange_cus_id(self,cr,uid,ids,customer_id,context = None):
		print "customer_idcustomer_idcustomer_idcustomer_id",customer_id
		cus_obj = self.pool.get("res.partner")
		cus_rec = cus_obj.browse(cr,uid,customer_id)
		print "cus_rec.streetcus_rec.streetcus_rec.street",cus_rec.name
		tot_add = (cus_rec.street or '')+ ' ' + (cus_rec.street2 or '') + '\n'+(cus_rec.city or '')+ ',' +(cus_rec.state_id.name or '') + '-' +(cus_rec.zip or '') + '\nPh:' + (cus_rec.phone or '')+ '\n' +(cus_rec.mobile or '')		
		return {'value':{'cus_address':tot_add}}

	def entry_confirm(self, cr, uid, ids,context=None):
		obj_rec = self.browse(cr, uid, ids[0])
		sale_line_obj = self.pool.get("kite.sale.order.line")
		for val in obj_rec.line_ids:
			if val.order_qty ==0:
				raise osv.except_osv(_('Warning!'),
				_('You cannot allowed to confirm with 0 order qty for product %s')%(val.product_id.name_template))
			if val.unit_price ==0:
				raise osv.except_osv(_('Warning!'),
				_('You cannot allowed to confirm with 0 Unit Price for product %s')%(val.product_id.name_template))
			val.write({'pending_qty':val.order_qty})
		tot = 0
		for deb in obj_rec.line_ids_debit:
			tot += deb.sub_total
		self.write(cr,uid,ids[0],{'state':'confirm','amount_total':obj_rec.amount_total - tot })								  
		remain_qty =((val.sale_line.inv_pending_qty - val.order_qty))
		if remain_qty >0:
			remain_qty =remain_qty
		else:
			remain_qty =0		

		sale_line_obj.write(cr, uid,val.sale_line.id, {'inv_pending_qty': remain_qty})	
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
		return super(kite_invoice, self).create(cr, uid, vals, context=context)
		
	def write(self, cr, uid, ids, vals, context=None):
		vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),'update_user_id':uid})
		return super(kite_invoice, self).write(cr, uid, ids, vals, context)		
	
	
	
kite_invoice()

class kite_invoice_line(osv.osv):
	
	_name = "kite.invoice.line"


	_columns = {
	
	
		'header_id':fields.many2one('kite.invoice', 'Inv No', required=1, ondelete='cascade'),
		'remark': fields.text('Remarks'),
		
		'name': fields.related('header_id','name',type='char', string='SO No'),
		'customer_id': fields.related('header_id','customer_id', type='many2one',relation='res.partner', string='Customer Name', store=True),
		'delivery_date': fields.date('Delivery Date', required=True),
		'order_qty': fields.float('Order Qty',required=True),
		'unit_price': fields.float('Unit Price',required=True),
		'sub_total': fields.float('Sub Total',readonly=True),
		'cus_price': fields.float('Customer PO Unit Price',required=True),
		
		
		'product_id':fields.many2one('product.product','Item Name',required=True),		
		'sale_line':fields.many2one('kite.sale.order.line','Sale Line'),		
		
		
		
		}




	
kite_invoice_line()

class kite_invoice_debit(osv.osv):
	
	_name = "kite.invoice.debit"


	_columns = {
	
	
		'header_id':fields.many2one('kite.invoice', 'Inv No', required=1, ondelete='cascade'),
		'remark': fields.text('Remarks'),
		
		'product_id':fields.many2one('product.product','Item Name',required=True),		
		'order_qty': fields.float('Order Qty',required=True),
		'unit_price': fields.float('Unit Price',required=True),
		'sub_total': fields.float('Sub Total',readonly=True),		
		
		'debit_id':fields.many2one('kite.debit','Debit No'),		
		
		
		
		}

kite_invoice_debit()

