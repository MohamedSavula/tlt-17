# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from odoo import api, fields, models, _


class StockReturnPickingInherit(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        new_picking, pick_type_id = super(StockReturnPickingInherit, self)._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        picking.purchase_id.return_picking = True
        return new_picking, pick_type_id


class purchase_order(models.Model):
    _inherit = "purchase.order"
    
#    check partial paid flag after complet
    
    def _compute_invoiced(self):
        for purchase in self:
            invoice_partial_flag = False
            invoice_status_new_flag = False
            if purchase.invoice_ids:
                a=0
                inv_len = len(purchase.invoice_ids)
                for invoice in purchase.invoice_ids:
                    if invoice.payment_state == 'paid':
                        a += 1
                if inv_len == a:
                    invoice_status_new_flag = True
                else:
                    count = 0
                    for invoice in purchase.invoice_ids:
                        if invoice.state == 'posted' and invoice.amount_residual < invoice.amount_total: 
                            invoice_partial_flag = True
            purchase.invoice_partial = invoice_partial_flag
            purchase.invoice_status_new = invoice_status_new_flag

    def _compute_invoiced_open(self):
        for purchase in self:
            purchase.invoice_open = False
            if purchase.invoice_ids:
                a=0
                inv_len = len(purchase.invoice_ids)
                for invoice in purchase.invoice_ids:
                    if invoice.state == 'draft':
                        a += 1
                if inv_len == a:
                    purchase.invoice_open = True
#                    
#                
    def _compute_shiped(self):
        for purchase in self:
            ship_status_flag = False
            ship_partial_flag = False
            if purchase.picking_ids:
                a=0
                picking_len = len(purchase.picking_ids)
                for picking in purchase.picking_ids:
                    if picking.state == 'done':
                        a += 1
                if picking_len == a:
                    ship_status_flag = True
                if a != 0 and not picking_len == a:
                    ship_partial_flag = True
            purchase.ship_status = ship_status_flag
            purchase.ship_partial = ship_partial_flag

    invoice_open = fields.Boolean(string='Invoiced', compute='_compute_invoiced_open',search='_search_open_invoice')
    invoice_status_new = fields.Boolean(string='Paid', compute='_compute_invoiced', search='_search_full_paid_invoice')
    invoice_partial = fields.Boolean(string='Partial Paid', compute='_compute_invoiced', search='_search_partial_paid_invoice',copy=False)
    ship_status = fields.Boolean(string='Received',compute='_compute_shiped',copy=False, search='_search_full_shipment')
    ship_partial = fields.Boolean(string='Partial Received',compute='_compute_shiped',copy=False, search='_search_partial_shipment')
    return_picking = fields.Boolean(string='Returned', copy=False, readonly=True)

    # @api.depends('picking_ids')
    # def get_return_picking(self):
    #     for rec in self:
    #         rec.return_picking = True if any()
    #
    
    def _search_full_shipment(self, operator, value):
        purchase_order = self.env['purchase.order'].search([])
        purchase_ids = []
        for purchase in purchase_order:
            if operator == '=':
                if purchase.picking_ids:
                    a=0
                    picking_len = len(purchase.picking_ids)
                    for picking in purchase.picking_ids:
                        if picking.state == 'done':
                            a += 1
                    if picking_len == a:
                        purchase_ids.append(purchase.id)
            else:
                if purchase.picking_ids:
                    a=0
                    picking_len = len(purchase.picking_ids)
                    for picking in purchase.picking_ids:
                        if picking.state != 'done':
                            a += 1
                    if picking_len == a:
                        purchase_ids.append(purchase.id)
                if not purchase.picking_ids:
                    purchase_ids.append(purchase.id)
        return [('id', 'in', purchase_ids)]
        
    def _search_partial_shipment(self, operator, value):
        purchase_order = self.env['purchase.order'].search([])
        purchase_ids = []
        for purchase in purchase_order:
            if operator == '=':
                if purchase.picking_ids:
                    a=0
                    picking_len = len(purchase.picking_ids)
                    for picking in purchase.picking_ids:
                        if picking.state == 'done':
                            a += 1
                    if a != 0 and picking_len != a:
                        purchase_ids.append(purchase.id)
            else:
                if purchase.picking_ids:
                    a=0
                    picking_len = len(purchase.picking_ids)
                    for picking in purchase.picking_ids:
                        if picking.state != 'done':
                            a += 1
                    if picking_len == a:
                        purchase_ids.append(purchase.id)
                if not purchase.picking_ids:
                    purchase_ids.append(purchase.id)
    
        return [('id', 'in', purchase_ids)]
#        
#        
#    
    def _search_partial_paid_invoice(self, operator, value):
        purchase_order = self.env['purchase.order'].search([])
        purchase_ids = []
        for purchase in purchase_order:
            if operator == '=':
                if purchase.invoice_ids:
                    a=0
                    inv_len = len(purchase.invoice_ids)
                    for invoice in purchase.invoice_ids:
                        if invoice.state == 'posted' and invoice.payment_state != 'paid' and invoice.amount_residual < invoice.amount_total:
                            a += 1
                    if a != 0:
                        purchase_ids.append(purchase.id)
            else:
                if purchase.invoice_ids:
                    a=0
                    for invoice in purchase.invoice_ids:
                        if invoice.state != 'posted':
                            purchase_ids.append(purchase.id)
                if not purchase.invoice_ids:
                    purchase_ids.append(purchase.id)
                
        return [('id', 'in', purchase_ids)]
#        
#        
    def _search_full_paid_invoice(self, operator, value):
        purchase_order = self.env['purchase.order'].search([])
        purchase_ids = []
        for purchase in purchase_order:
            if operator == '=':
                if purchase.invoice_ids:
                    a=0
                    inv_len = len(purchase.invoice_ids)
                    for invoice in purchase.invoice_ids:
                        if invoice.payment_state == 'paid':
                            a += 1
                    if inv_len == a:
                        purchase_ids.append(purchase.id)
            else:
                if purchase.invoice_ids:
                    for invoice in purchase.invoice_ids:
                        if invoice.payment_state != 'paid':
                            purchase_ids.append(purchase.id)
                if not purchase.invoice_ids:
                    purchase_ids.append(purchase.id)
        return [('id', 'in', purchase_ids)]
#        

    @api.depends('invoice_ids','state')
    def _search_open_invoice(self, operator, value):
        purchase_order = self.env['purchase.order'].search([])
        purchase_ids = []
        if operator == '=':
            for purchase in purchase_order:
                if purchase.invoice_ids:
                    a=0
                    inv_len = len(purchase.invoice_ids)
                    for invoice in purchase.invoice_ids:
                        if invoice.state == 'draft':
                            a += 1
                    if inv_len == a:
                        purchase_ids.append(purchase.id)
        else:
            for purchase in purchase_order:
                if purchase.invoice_ids:
                    a=0
                    inv_len = len(purchase.invoice_ids)
                    for invoice in purchase.invoice_ids:
                        if invoice.state != 'draft':
                            purchase_ids.append(purchase.id)
                if not purchase.invoice_ids:
                    purchase_ids.append(purchase.id)
        return [('id', 'in', purchase_ids)]
#    
#    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
