# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockLocationInherit(models.Model):
    _inherit = 'stock.location'

    negative_stock = fields.Boolean(string="Don't allow negative stock")
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('order_line', 'order_line.product_id')
    def get_analytic_account_from_location(self):
        for rec in self:
            for line in rec.order_line:
                line.analytic_distribution = {rec.picking_type_id.default_location_dest_id.account_analytic_id.id: 100}


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for rec in self:
            for line in rec.move_line_ids_without_package:
                if line.location_id.negative_stock:
                    stock_quant = sum(list(self.env['stock.quant'].search(
                        [('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id)]).mapped(
                        'quantity')))
                    if round(stock_quant, 3) < round(line.qty_done, 3):
                        raise UserError(_("QTY available in  %s ---> %s" % (line.product_id.name, stock_quant)))
        res = super(StockPickingInherit, self).button_validate()
        return res


class MrpProductionInherit(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        for rec in self:
            for line in rec.move_raw_ids:
                if line.location_id.negative_stock:
                    stock_quant = sum(list(self.env['stock.quant'].search(
                        [('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id)]).mapped(
                        'quantity')))
                    if round(stock_quant, 3) < round(line.product_uom_qty, 3):
                        raise UserError(_("QTY available in  %s ---> %s" % (line.product_id.name, stock_quant)))
        res = super(MrpProductionInherit, self).button_mark_done()
        return res
