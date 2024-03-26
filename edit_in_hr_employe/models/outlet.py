# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OutletConfigEmployee(models.Model):
    _name = 'outlet'
    _description = "OutletConfigEmployee"

    name = fields.Char(string="Outlet", required=True, )
