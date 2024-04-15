# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    seq = fields.Char()

    @api.constrains('name', 'partner_id', 'po_attach_id', "invoice_line_ids")
    def get_print_seq(self):
        for rec in self:
            rec.seq = self.env['ir.sequence'].next_by_code('print_seq')

    def get_tax_to_print(self):
        tax_amount_group = 0
        for rec in self:
            if rec.invoice_line_ids.tax_ids:
                tax_ids = rec.invoice_line_ids.mapped('tax_ids')
                filtered_tax_ids = tax_ids.filtered(lambda tax: tax.tax_group_id.id == 2)
                if filtered_tax_ids:
                    tax_amount_group = abs(filtered_tax_ids[0].amount)
        return tax_amount_group
