# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    # Allowance
    basic_salary = fields.Integer(string="Basic Salary")
    incentives = fields.Integer(string="Transportation Gouna")
    transportation = fields.Integer(string="Transportation")
    risk_allowance = fields.Integer(string="Risk Allowance")
    other = fields.Integer(string="Other")
    housing_allowance = fields.Float(string="Housing Allowance")
    telephone_allowance = fields.Float(string="Telephone Allowance")
    meal_allowance = fields.Float(string="Meal Allowance")
    # Deduction
    social_insurance = fields.Integer(string="Social Insurance")
    telephone = fields.Integer(string="Attendance")
    medical_insurance = fields.Integer(string="Medical Insurance")
    c_l = fields.Float(string="C/L")
    salary_advance_customize = fields.Float(string="Salary Advance")
    loans = fields.Float(string="Loans")
    other_deduction = fields.Float(string="Other Deduction")
    # Total
    net_salary_customize = fields.Float(string="Net Salary", compute="sum_net_salary", store=True)
    net_gross_salary = fields.Float(string="Gross Salary", compute="sum_net_salary", store=True)
    # Basic Salary
    basic_salary_customize = fields.Float(string="Basic Salary")
    s_charge_12 = fields.Float(string="S.Charge 12%")
    add_years = fields.Float(string="الزيادة السنوية")
    work_location_id = fields.Many2one(related='employee_id.work_location_id', store=True)

    @api.depends('wage', 'incentives', 'transportation', 'risk_allowance', 'other', 'housing_allowance',
                 'telephone_allowance', 'meal_allowance', 'social_insurance', 'telephone', 'medical_insurance', 'c_l',
                 'salary_advance_customize', 'loans', 'other_deduction', 'add_years')
    def sum_net_salary(self):
        for rec in self:
            allowance = rec.incentives + rec.transportation + rec.other + rec.housing_allowance + rec.telephone_allowance + rec.meal_allowance
            deduction = rec.social_insurance + rec.telephone + rec.medical_insurance + rec.c_l + rec.salary_advance_customize + rec.loans + rec.other_deduction
            rec.net_salary_customize = rec.wage + rec.add_years + allowance - deduction
            rec.net_gross_salary = rec.wage + allowance + rec.add_years
            if rec.wage > 0:
                rec.basic_salary_customize = rec.wage / 2
                rec.s_charge_12 = rec.wage / 2


class HrPayrollStructureInherit(models.Model):
    _inherit = 'hr.payroll.structure'

    type_structure = fields.Selection(selection=[('production', 'Production'), ('employee', 'Employee')])


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    net_gross_salary = fields.Float(string="Gross Salary", compute="get_net_gross_salary", store=True)

    def update_get_net_gross_salary(self):
        for rec in self.search([]):
            rec.get_net_gross_salary()

    @api.depends('line_ids')
    def get_net_gross_salary(self):
        for rec in self:
            rec.net_gross_salary = rec.line_ids.filtered(lambda l: l.code == 'GROSS' or l.code == 'GROSS_P').amount

    def _compute_basic_net(self):
        line_values = (self._origin)._get_line_values(['BASIC', 'NET'])
        line_values_p = (self._origin)._get_line_values(['BASIC_P', 'NET_P'])
        for payslip in self:
            if payslip.struct_id.type_structure == 'employee':
                payslip.basic_wage = line_values['BASIC'][payslip._origin.id]['total']
                payslip.net_wage = line_values['NET'][payslip._origin.id]['total']
            elif payslip.struct_id.type_structure == 'production':
                payslip.basic_wage = line_values_p['BASIC_P'][payslip._origin.id]['total']
                payslip.net_wage = line_values_p['NET_P'][payslip._origin.id]['total']
            else:
                payslip.basic_wage = payslip.basic_wage
                payslip.net_wage = payslip.net_wage
