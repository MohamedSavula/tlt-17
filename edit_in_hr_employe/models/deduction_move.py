# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DeductionConfigEmployeeMove(models.Model):
    _name = 'deduction.move'
    _description = "deductionConfigEmployeeMove"

    d_deduction_id = fields.Many2one(comodel_name="deduction", string="Deduction", required=False, )
    d_code = fields.Char(string="Code", required=False, related='d_deduction_id.code')
    d_amount = fields.Float(string="Amount", required=False, )
    d_move_id = fields.Many2one(comodel_name="hr.contract", string="", required=False, )
