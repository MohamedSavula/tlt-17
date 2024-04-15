# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    bank_or_cash = fields.Selection(string="Bank Or Cash", selection=[('bank', 'Bank'), ('cash', 'Cash')])


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    bank_or_cash = fields.Selection(related="employee_id.bank_or_cash", store=True)
