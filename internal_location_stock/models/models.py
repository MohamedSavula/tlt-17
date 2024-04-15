# -*- coding: utf-8 -*-

from odoo import models


class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'

    def internal_location_stock(self):
        lines = [(0, 0, {
            "product_id": line.product_id.id,
            "name": line.product_id.name,
            "product_uom_qty": line.quantity,
            'product_uom': line.product_uom_id.id,
        }) for line in self]
        return {
            'name': 'Internal Transfer',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'context': {
                'default_picking_type_id': self[0].location_id.warehouse_id.int_type_id.id,
                'default_move_ids_without_package': lines
            },
        }

    def create_sale_order(self):
        lines = [(0, 0, {
            "product_id": line.product_id.id,
            "name": line.product_id.display_name,
            "product_uom_qty": line.quantity,
            'product_uom': line.product_uom_id.id,
        }) for line in self]
        return {
            'name': 'Internal Transfer',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'context': {
                'default_order_line': lines
            },
        }
