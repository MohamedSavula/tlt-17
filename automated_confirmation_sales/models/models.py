# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    automated_confirmation = fields.Boolean(copy=False)


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        for rec in self:
            if rec.picking_ids and rec.company_id.automated_confirmation:
                rec.picking_ids.button_validity_customize()
                if rec.picking_ids[0].state == 'done':
                    self.env['sale.advance.payment.inv'].sudo().with_context(active_ids=self.ids).create(
                        {}).create_invoices()
                    rec.invoice_ids.action_post()
        return res
