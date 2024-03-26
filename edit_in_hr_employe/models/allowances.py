# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AllowancesConfigEmployee(models.Model):
    _name = 'allowances'
    _description = "AllowancesConfigEmployee"

    name = fields.Char(string="Name", required=True)
    code = fields.Char()
