# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    partner_field_mandatory = fields.Boolean(string="", default=True, )

    def action_post(self):
        for rec in self:
            if rec.move_type == "entry" and rec.partner_field_mandatory and rec.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.type in (
                    "payable", "receivable") and not line.partner_id):
                raise UserError(_('Please Fill Partner Field'))
        return super(AccountMoveInh, self).action_post()
