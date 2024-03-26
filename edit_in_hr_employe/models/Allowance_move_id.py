# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AllowancesConfigEmployeeMove(models.Model):
    _name = 'allowances.move'
    _description = "AllowancesConfigEmployeeMove"

    a_allowance_id = fields.Many2one(comodel_name="allowances", string="Allowances", required=False, )
    a_code = fields.Char(string="Code", required=False, related='a_allowance_id.code')
    a_amount = fields.Float(string="Amount", required=False, )
    a_move_id = fields.Many2one(comodel_name="hr.contract", string="", required=False, )
