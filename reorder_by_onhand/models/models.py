# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.tools import float_compare



class StockWarehouseOrderpointInherit(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.depends('qty_multiple', 'qty_forecast', 'qty_on_hand', 'product_min_qty', 'product_max_qty')
    def _compute_qty_to_order(self):
        for orderpoint in self:
            if not orderpoint.product_id or not orderpoint.location_id:
                orderpoint.qty_to_order = False
                continue
            qty_to_order = 0.0
            rounding = orderpoint.product_uom.rounding
            if float_compare(orderpoint.qty_on_hand, orderpoint.product_min_qty, precision_rounding=rounding) < 0:
                qty_to_order = max(orderpoint.product_min_qty, orderpoint.product_max_qty) - orderpoint.qty_on_hand

                remainder = orderpoint.qty_multiple > 0 and qty_to_order % orderpoint.qty_multiple or 0.0
                if float_compare(remainder, 0.0, precision_rounding=rounding) > 0:
                    qty_to_order += orderpoint.qty_multiple - remainder
            orderpoint.qty_to_order = qty_to_order
