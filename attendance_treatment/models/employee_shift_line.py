# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class EmployeeShiftLine(models.Model):
    _inherit = 'employee.shift.line'

    shift_name = fields.Selection([
        ('shift_s', '08 - 16 or 9 - 17'),
        ('shift_20', '20 - 08'),
        ('shift_24', '00 - 08'),
        ('shift_16', '16 - 00'),
    ])
