# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    shift_name_ids = fields.One2many(comodel_name="employee.shift.line", inverse_name="shift_name_id")
    the_coefficient = fields.Float(string="The Coefficient")

    def unlink_shifts(self):
        for employee in self.search([]):
            employee.shift_name_ids.unlink()

    def get_fin_product(self):
        pass


class EmployeeShiftLine(models.Model):
    _name = 'employee.shift.line'

    name = fields.Char(string="", required=False, )
    shift_name = fields.Many2one('shift.name', string="Shift Name")
    shift_name_id = fields.Many2one('hr.employee', string="")
    shift_payroll_id = fields.Many2one('hr.payslip', string="")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date TO")
    hour_from = fields.Float(string="Hour From")
    hour_to = fields.Float(string="Hour To")


class ShiftName(models.Model):
    _name = 'shift.name'

    name = fields.Char(string="Shift Name")
    number = fields.Integer(string="Number")
