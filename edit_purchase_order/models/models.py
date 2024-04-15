# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.osv import expression


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To',
                                      required=True, default=False,
                                      domain="['|', ('warehouse_id', '=', False), ('warehouse_id.company_id', '=', company_id)]",
                                      help="This will determine operation type of incoming shipment")
    non_purchase_order = fields.Boolean(string="Non Purchase Order", default=False)
    is_approve_confirm = fields.Boolean()
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('approve', 'Approved'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    invoice_status = fields.Selection([
        ('no', 'Nothing to Bill'),
        ('to invoice', 'Waiting Bills'),
        ('invoiced', 'Fully Billed'),
        ('closed', 'closed'),
    ], string='Billing Status', compute='_get_invoiced', store=True, readonly=True, copy=False, default='no')

    def close_invoice_status(self):
        for rec in self:
            rec.invoice_status = 'closed'

    def go_approve_confirm(self):
        for rec in self:
            for line in rec.order_line:
                location = line.order_id.picking_type_id.default_location_dest_id
                on_hand = self.env['stock.quant'].sudo().search(
                    [('product_id', '=', line.product_id.id), ('location_id', '=', location.id)],
                    limit=1).quantity
                max_location = line.product_id.product_tmpl_id.min_quantity_ids.filtered(
                    lambda l: l.location_id == location)
                quantity = line.product_qty
                if max_location:
                    max_qty = max_location[0].max_quantity
                    if quantity + on_hand > max_qty:
                        raise UserError("This product (%s) max quantity (%s) in the location [%s] on hand (%s)" % (
                            line.product_id.display_name, max_qty, location.display_name, on_hand))
            rec.is_approve_confirm = True
            rec.state = 'approve'

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'approve']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
            for line in order.order_line:
                line.product_id.last_product_price = line.price_unit_customize
                line.product_id.product_tmpl_id.last_product_price = line.price_unit_customize
        return True

    @api.onchange('company_id')
    def _onchange_company_id(self):
        pass


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    last_product_price = fields.Float(string="Last Price")


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    last_product_price = fields.Float(string="Last Price")


class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    price_unit_customize = fields.Float(string='Unit Price', )
    discount_percent = fields.Float(string='Discount Percent', )
    discount_amount = fields.Float(string='Discount Amount', )
    last_purchase_price = fields.Float(string="Last Price", compute="get_last_purchase_price", store=True)
    product_qty = fields.Float(string='Quantity', digits=(12, 2), required=True)

    @api.depends('product_id')
    def get_last_purchase_price(self):
        for rec in self:
            rec.last_purchase_price = self.env['purchase.order.line'].sudo().search(
                [('order_id.state', 'in', ['purchase', 'done']), ('product_id', '=', rec.product_id.id)],
                limit=1).price_unit_customize

    @api.onchange('price_unit_customize', 'discount_amount')
    def get_discount_percent(self):
        for rec in self:
            if rec.price_unit_customize:
                rec.discount_percent = rec.discount_amount / rec.price_unit_customize * 100

    @api.onchange('price_unit_customize', 'discount_percent')
    def get_discount_amount(self):
        for rec in self:
            if rec.price_unit_customize:
                rec.discount_amount = (rec.discount_percent / 100) * rec.price_unit_customize

    @api.onchange('product_id', 'price_unit')
    def get_price_unit_tlt(self):
        for rec in self:
            if not rec.price_unit_customize:
                rec.price_unit_customize = rec.price_unit
                rec.get_discount_percent()
                rec.get_discount_amount()

    @api.onchange('price_unit_customize', 'discount_percent', 'discount_percent', 'product_qty')
    def get_price_unit_finish(self):
        for rec in self:
            rec.price_unit = rec.price_unit_customize - rec.discount_amount


class PurchaseBillUnionInherit(models.Model):
    _inherit = 'purchase.bill.union'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, order=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('reference', operator, name)]
        purchase_bills_union_ids = self._search(expression.AND([domain, args]), limit=limit)
        return purchase_bills_union_ids
