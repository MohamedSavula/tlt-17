# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class stock_quant(models.Model):
    _inherit = 'stock.quant'

    categ_id = fields.Many2one('product.category', 'Product Category', store=True, related="product_id.categ_id")

    @api.model_create_multi
    def create(self, vals):
        """ Override to handle the "inventory mode" and create a quant as
        superuser the conditions are met.
        """
        if self._is_inventory_mode() and any(
                f in vals for f in ['inventory_quantity', 'inventory_quantity_auto_apply']):
            allowed_fields = self._get_inventory_fields_create()
            if any(field for field in vals.keys() if field not in allowed_fields):
                return super(stock_quant, self).create(vals)

            auto_apply = 'inventory_quantity_auto_apply' in vals
            inventory_quantity = vals.pop('inventory_quantity_auto_apply', False) or vals.pop(
                'inventory_quantity', False) or 0
            product = self.env['product.product'].browse(vals['product_id'])
            location = self.env['stock.location'].browse(vals['location_id'])
            lot_id = self.env['stock.production.lot'].browse(vals.get('lot_id'))
            package_id = self.env['stock.quant.package'].browse(vals.get('package_id'))
            owner_id = self.env['res.partner'].browse(vals.get('owner_id'))
            quant = self._gather(product, location, lot_id=lot_id, package_id=package_id, owner_id=owner_id,
                                 strict=True)
            if lot_id:
                quant = quant.filtered(lambda q: q.lot_id)
            if quant:
                quant = quant[0].sudo()
            else:
                return super(stock_quant, self).create(vals)
            if auto_apply:
                quant.write({'inventory_quantity_auto_apply': inventory_quantity})
            else:
                quant.inventory_quantity = inventory_quantity
                quant.user_id = vals.get('user_id', self.env.user.id)
                quant.inventory_date = fields.Date.today()
            return quant
        return super(stock_quant, self).create(vals)


class stock_move_line(models.Model):
    _inherit = 'stock.move.line'

    categ_id = fields.Many2one('product.category', 'Product Category', store=True, related="product_id.categ_id")

    scheduled_date = fields.Datetime(required=False, related="picking_id.scheduled_date")
