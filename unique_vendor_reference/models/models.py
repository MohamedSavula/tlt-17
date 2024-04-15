# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    @api.constrains('partner_id', 'partner_ref')
    def unique_vendor_reference(self):
        for rec in self:
            vendor_reference = self.search(
                [('partner_id', '=', rec.partner_id.id), ('partner_ref', '=', rec.partner_ref),
                 ('partner_ref', '!=', False), ('id', '!=', rec.id)])
            if vendor_reference:
                raise UserError(
                    "Duplicated vendor reference detected. You probably encoded twice the same vendor ( %s ), purchase number( %s )" % (
                        vendor_reference.partner_id.name, vendor_reference.name))


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    @api.constrains('partner_id', 'ref')
    def unique_vendor_reference(self):
        for rec in self:
            vendor_reference = self.search(
                [('move_type', '=', 'in_invoice'), ('partner_id', '=', rec.partner_id.id),
                 ('ref', '=', rec.ref),
                 ('ref', '!=', False), ('id', '!=', rec.id)])
            if vendor_reference:
                raise UserError(
                    "Duplicated vendor reference detected. You probably encoded twice the same vendor ( %s ), Bill( %s )" % (
                        vendor_reference.partner_id.name, vendor_reference.name))
