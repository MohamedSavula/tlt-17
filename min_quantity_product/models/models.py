# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    is_validity = fields.Boolean(copy=False, default=False)

    def button_validity_customize(self):
        for rec in self:
            rec.action_set_quantities_to_reservation()
            rec.action_assign()
            for line in rec.move_line_ids_without_package:
                on_hand = self.env['stock.quant'].sudo().search(
                    [('product_id', '=', line.product_id.id), ('location_id', '=', line.location_dest_id.id)],
                    limit=1).quantity
                max_location = line.product_id.product_tmpl_id.min_quantity_ids.filtered(
                    lambda l: l.location_id == rec.location_dest_id)
                demand = line.product_uom_qty
                if max_location:
                    max_qty = max_location[0].max_quantity
                    if demand + on_hand > max_qty:
                        user = []
                        for x in self.env.ref('min_quantity_product.id_group_min_quantity').users:
                            user.append(x.id)
                        if self.env.user.id not in user:
                            raise UserError("This product (%s) max quantity (%s) in the location [%s] on hand (%s)" % (
                                line.product_id.display_name, max_qty, line.location_dest_id.display_name, on_hand))
            return rec.button_validate()


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    min_quantity_ids = fields.One2many(comodel_name="min.quantity", inverse_name="product_id")
    company_ids = fields.Many2many(comodel_name="res.company", string="Companies")


class MinQuantity(models.Model):
    _name = 'min.quantity'
    _description = 'Min Quantity'

    product_id = fields.Many2one('product.template')
    location_id = fields.Many2one('stock.location', string='Location', required=True)
    min_quantity = fields.Float(string="Min Quantity", required=True)
    max_quantity = fields.Float(string="Max Quantity", required=False)


class PurchaseRequisitionInherit(models.Model):
    _inherit = 'purchase.requisition'

    def check_min_quantity(self):
        for rec in self:
            location = rec.location_dest_id
            for line in rec.line_ids:
                if line.product_qty > 0:
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

    def action_in_progress(self):
        res = super().action_in_progress()
        self.check_min_quantity()
        return res

    def action_open(self):
        self.check_min_quantity()
        return super().action_open()

    def transfer_approve(self):
        self.check_min_quantity()
        return super().transfer_approve()

    def create_transfer(self):
        self.check_min_quantity()
        return super().create_transfer()
