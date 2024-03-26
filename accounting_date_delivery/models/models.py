# -*- coding: utf-8 -*-

from odoo import models, fields


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    accounting_date = fields.Date(copy=False)


class stock_move(models.Model):
    _inherit = 'stock.move'

    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        res = super(stock_move, self)._prepare_account_move_vals(credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost)
        res.update({
            'date': self.picking_id.accounting_date if self.picking_id.accounting_date else self._context.get('force_period_date', fields.Date.context_today(self))
        })
        return res
