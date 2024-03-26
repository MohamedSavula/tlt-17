# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DeductionConfigEmployee(models.Model):
    _name = 'deduction'
    _description = "DeductionConfigEmployee"

    name = fields.Char(required=True)
    code = fields.Char()
