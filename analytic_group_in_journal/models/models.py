# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    tax_vat = fields.Float(string="VAT 14%", compute="get_tax_vat_and_tax_with", store=True)
    tax_with = fields.Float(string="Withholding", compute="get_tax_vat_and_tax_with", store=True)

    @api.depends('invoice_line_ids', 'name', 'line_ids')
    def get_tax_vat_and_tax_with(self):
        for rec in self:
            rec.tax_vat = sum(rec.line_ids.mapped('tax_vat'))
            rec.tax_with = sum(rec.line_ids.mapped('tax_with'))


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    group_id = fields.Many2one('account.analytic.group', string='Group')
    tax_vat = fields.Float(string="VAT 14%", required=False, compute="get_tax_vat_and_tax_with", store=True)
    tax_with = fields.Float(string="Withholding", required=False, compute="get_tax_vat_and_tax_with", store=True)

    @api.depends('tax_ids', 'price_subtotal')
    def get_tax_vat_and_tax_with(self):
        for rec in self:
            rec.tax_vat = 0
            rec.tax_with = 0
            for tax in rec.tax_ids:
                if tax.tax_group_id.name == 'VAT':
                    rec.tax_vat = tax.amount * rec.price_subtotal / 100
                elif tax.tax_group_id.name == 'Withholding Tax':
                    rec.tax_with = tax.amount * rec.price_subtotal / 100
