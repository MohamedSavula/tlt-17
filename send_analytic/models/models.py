# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAnalyticTag(models.Model):
    _name = 'account.analytic.tag'
    _description = 'Account Analytic Tag'

    name = fields.Char(required=True)
    code = fields.Char()


class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')


class StockMoveInherit(models.Model):
    _inherit = "stock.move"

    analytic_account_id = fields.Many2one(string='Analytic Account', comodel_name='account.analytic.account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
        self.ensure_one()
        res = super(StockMoveInherit, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id,
                                                                       description)
        if not self.analytic_account_id or not res:
            return res
        for num in range(0, 2):
            if res[num][2]["account_id"] != self.product_id.categ_id.property_stock_valuation_account_id.id:
                res[num][2].update({
                    'analytic_distribution': {self.analytic_account_id.id: 100},
                    'analytic_tag_ids': self.analytic_tag_ids.ids,
                })
        return res

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        res = super()._prepare_merge_moves_distinct_fields()
        res.append('analytic_account_id')
        res.append('analytic_tag_ids')
        return res


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    analytic_account_id = fields.Many2one(
        related='move_id.analytic_account_id')
    analytic_tag_ids = fields.Many2many(
        related='move_id.analytic_tag_ids')


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        for rec in self:
            rec.picking_ids.move_ids_without_package.update({
                'analytic_account_id': rec.analytic_account_id.id
            })
        return res
