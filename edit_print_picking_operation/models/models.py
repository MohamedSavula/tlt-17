# -*- coding: utf-8 -*-

from odoo import models, fields


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    user_cancel_id = fields.Many2one(comodel_name="res.users")

    def action_cancel(self):
        res = super().action_cancel()
        for rec in self:
            rec.user_cancel_id = self.env.user.id
        return res