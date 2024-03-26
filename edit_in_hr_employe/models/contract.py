# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EditInHrContract(models.Model):
    _inherit = 'hr.contract'
    _description = "edit_In_hr.contract"

    allowances_ids = fields.One2many(comodel_name="allowances.move", inverse_name="a_move_id")
    deduction_ids = fields.One2many(comodel_name="deduction.move", inverse_name="d_move_id")
