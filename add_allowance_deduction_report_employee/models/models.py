# -*- coding: utf-8 -*-

from odoo import models, fields


class HrContractEmployeeReportInherit(models.Model):
    _inherit = "hr.contract.employee.report"

    # Allowance
    basic_salary = fields.Integer(string="Basic Salary", group_operator="avg", readonly=True)
    incentives = fields.Integer(string="Incentives", group_operator="avg", readonly=True)
    transportation = fields.Integer(string="Transportation", group_operator="avg", readonly=True)
    risk_allowance = fields.Integer(string="Risk Allowance", group_operator="avg", readonly=True)
    other = fields.Integer(string="Other", group_operator="avg", readonly=True)
    housing_allowance = fields.Float(string="Housing Allowance", group_operator="avg", readonly=True)
    telephone_allowance = fields.Float(string="Telephone Allowance", group_operator="avg", readonly=True)
    meal_allowance = fields.Float(string="Meal Allowance", group_operator="avg", readonly=True)
    # Deduction
    social_insurance = fields.Integer(string="Social Insurance", group_operator="avg", readonly=True)
    telephone = fields.Integer(string="Telephone", group_operator="avg", readonly=True)
    medical_insurance = fields.Integer(string="Medical Insurance", group_operator="avg", readonly=True)
    c_l = fields.Float(string="C/L", group_operator="avg", readonly=True)
    salary_advance_customize = fields.Float(string="Salary Advance", group_operator="avg", readonly=True)
    loans = fields.Float(string="Loans", group_operator="avg", readonly=True)
    other_deduction = fields.Float(string="Other Deduction", group_operator="avg", readonly=True)

    def _query(self, fields='', from_clause='', outer=''):
        fields += """
            , c.basic_salary AS basic_salary
            , c.incentives AS incentives
            , c.transportation AS transportation
            , c.risk_allowance AS risk_allowance
            , c.other AS other
            , c.housing_allowance AS housing_allowance
            , c.telephone_allowance AS telephone_allowance
            , c.meal_allowance AS meal_allowance
            , c.social_insurance AS social_insurance
            , c.telephone AS telephone
            , c.medical_insurance AS medical_insurance
            , c.c_l AS c_l
            , c.salary_advance_customize AS salary_advance_customize
            , c.loans AS loans
            , c.other_deduction AS other_deduction
            """
        return super(HrContractEmployeeReportInherit, self)._query(fields, from_clause, outer)
