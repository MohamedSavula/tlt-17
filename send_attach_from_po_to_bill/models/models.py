# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    po_attach_id = fields.Many2one(comodel_name="purchase.order", string="Purchase order")

    @api.constrains('po_attach_id')
    def get_attach_from_po(self):
        attachments = self.env['ir.attachment'].search(
            [('res_model', '=', 'purchase.order'), ('res_id', '=', self.po_attach_id.id)])
        for attachment in attachments:
            attachment.copy({
                'res_model': 'account.move',
                'res_id': self.id,
            })


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res['po_attach_id'] = self.id
        return res
