# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta

from odoo.exceptions import UserError


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            rec.address_home_id = self.env['res.partner'].sudo().create({
                'name': rec.name,
                'type': 'contact',
                'is_company': False,
            })
        return res


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    loans_id = fields.Many2one(comodel_name="loans")
    salary_advance_id = fields.Many2one(comodel_name="salary.advance")
    cl_salary_advance_id = fields.Many2one(comodel_name="cl.salary.advance")

    def action_post(self):
        res = super(AccountMoveInherit, self).action_post()
        if self.loans_id:
            self.loans_id.confirm_action()
        if self.salary_advance_id:
            self.salary_advance_id.confirm_action()
        if self.cl_salary_advance_id:
            self.cl_salary_advance_id.confirm_action()
        return res


class LoansAndAddvance(models.Model):
    _name = 'loans'
    _description = 'loans_Description'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    state = fields.Selection(
        [("draft", "Draft"), ("validate", "Validate"), ("confirmed", "Confirm"), ("close", "Closed")], readonly=True,
        default="draft",
        tracking=True)
    name = fields.Char('', readonly=True, copy=False, default='New', tracking=True)
    date = fields.Date("Date", tracking=True, required=True)
    deduction_date = fields.Date("Deduction Date", tracking=True, required=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee", required=True, tracking=True)
    amount = fields.Float(string="Amount", tracking=True, required=True)
    no_of_installment = fields.Integer(string="No Of Installment", tracking=True, default=1)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    loans_ids = fields.One2many('loans.line', 'loans_id', string="", readonly=True)
    # reason = fields.Text(string="Reason", tracking=True)
    journal_id = fields.Many2one('account.journal', string='Journal')
    account_id = fields.Many2one('account.account', string='Debit Account', compute='git_account_id_idd')
    account_idd = fields.Many2one('account.account', string='Credit Account', compute='git_account_id_idd')
    loan_id = fields.Many2one('hr.payslip', string='')
    journal_entry_id = fields.Many2one('account.move', string='', copy=False, readonly=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", related="employee_id.company_id",
                                 store=True)

    def update_deduction_date(self):
        for rec in self:
            for line in rec.loans_ids:
                if line.name and line.name > fields.Date.today():
                    new_date = line.name.replace(day=rec.deduction_date.day)
                    line.write({'name': new_date})

    def close(self):
        for rec in self:
            rec.state = "close"

    @api.onchange('employee_id')
    def get_journal(self):
        for rec in self:
            rec.journal_id = self.env['account.journal'].sudo().search(
                [('is_loan', '=', True), ('company_id', '=', rec.employee_id.company_id.id)], limit=1).id
        # return journal

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError("Can not delete")
        return super().unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('loans.loane') or 'New'
        result = super(LoansAndAddvance, self).create(vals)
        return result

    @api.depends('journal_id')
    def git_account_id_idd(self):
        for rec in self:
            rec.account_id = False
            rec.account_idd = False
            if rec.journal_id.account_ids and rec.journal_id.account_idd:
                rec.account_id = rec.journal_id.account_ids.id
                rec.account_idd = rec.journal_id.account_idd.id
            else:
                rec.account_id = False
                rec.account_idd = False

    def compute_installment(self):
        for rec in self:
            loan_line = []
            no_install = rec.no_of_installment
            rec.loans_ids = False
            date_date = rec.deduction_date
            for line in range(no_install):
                loan_line.append((0, 0, {
                    'name': date_date,
                    'amount': rec.amount / rec.no_of_installment,
                }))
                date_date = date_date + relativedelta(months=1)
            rec.loans_ids = loan_line

    def validate_action(self):
        for rec in self:
            rec.state = 'validate'
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'entry',
                'ref': rec.name,
                'partner_field_mandatory': False,
                'date': rec.deduction_date,
                'journal_id': self.journal_id.id,
                'loans_id': self.id,
                'line_ids': [(0, 0, {
                    'account_id': rec.account_id.id,
                    'name': rec.employee_id.name,
                    'partner_id': rec.employee_id.address_home_id.id,
                    'debit': rec.amount,
                }), (0, 0, {
                    'account_id': rec.account_idd.id,
                    'name': rec.employee_id.name,
                    'credit': rec.amount,
                })],
            })
            rec.journal_entry_id = invoice.id

    def confirm_action(self):
        for rec in self:
            rec.state = 'confirmed'


# loan model
class LoansAddvanceLine(models.Model):
    _name = 'loans.line'
    _description = 'loans_line'

    name = fields.Date('Payment Date')
    amount = fields.Float('Amount')
    loans_payslip_id = fields.Many2one('hr.payslip', string='')
    loans_id = fields.Many2one('loans', string='')


# salary advance model
class EditSalaryAdvance(models.Model):
    _name = 'salary.advance'
    _description = 'salary advance Description'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    state = fields.Selection(
        [("draft", "Draft"), ("validate", "Validate"), ("confirmed", "Confirm"), ("close", "Closed")], readonly=True,
        default="draft",
        tracking=True)
    name = fields.Char('', readonly=True, copy=False, default='New', tracking=True)
    date = fields.Date("Date", tracking=True, required=True)
    deduction_date = fields.Date("Deduction Date", tracking=True, required=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee", required=True, tracking=True)
    amount = fields.Float(string="Amount", tracking=True, required=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    journal_id = fields.Many2one('account.journal', string='Journal')
    account_id = fields.Many2one('account.account', string='Debit Account', compute='git_account_id_idd')
    account_idd = fields.Many2one('account.account', string='Credit Account', compute='git_account_id_idd')
    reason = fields.Text(string="Reason", tracking=True)
    salary_advance_id = fields.Many2one('hr.payslip', string='')
    journal_entry_id = fields.Many2one('account.move', string='', copy=False, readonly=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", related="employee_id.company_id",
                                 store=True)

    def close(self):
        for rec in self:
            rec.state = "close"

    @api.onchange('employee_id')
    def get_journal(self):
        for rec in self:
            rec.journal_id = self.env['account.journal'].sudo().search(
                [('is_salary_advance', '=', True), ('company_id', '=', rec.employee_id.company_id.id)], limit=1).id
        # return journal

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError("Can not delete")
        return super().unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('salary.advance') or 'New'
        result = super(EditSalaryAdvance, self).create(vals)
        return result

    @api.depends('journal_id')
    def git_account_id_idd(self):
        for rec in self:
            rec.account_id = False
            rec.account_idd = False
            if rec.journal_id.account_ids and rec.journal_id.account_idd:
                rec.account_id = rec.journal_id.account_ids.id
                rec.account_idd = rec.journal_id.account_idd.id
            else:
                rec.account_id = False
                rec.account_idd = False

    def validate_action(self):
        for rec in self:
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'entry',
                'date': rec.deduction_date,
                'partner_field_mandatory': False,
                'salary_advance_id': self.id,
                'ref': rec.name,
                'journal_id': self.journal_id.id,
                'line_ids': [(0, 0, {
                    'account_id': rec.account_id.id,
                    'name': rec.employee_id.name,
                    'partner_id': rec.employee_id.address_home_id.id,
                    'debit': rec.amount,
                }), (0, 0, {
                    'account_id': rec.account_idd.id,
                    'name': rec.employee_id.name,
                    'credit': rec.amount,
                })],
            })
            rec.journal_entry_id = invoice.id
            rec.state = 'validate'

    def confirm_action(self):
        for rec in self:
            rec.state = 'confirmed'


class ClSalaryAdvance(models.Model):
    _name = 'cl.salary.advance'
    _description = 'Cl salary Advance'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    state = fields.Selection(
        [("draft", "Draft"), ("validate", "Validate"), ("confirmed", "Confirm"), ("close", "Closed")], readonly=True,
        default="draft",
        tracking=True)
    name = fields.Char('', readonly=True, copy=False, default='New', tracking=True)
    date = fields.Date("Date", tracking=True, required=True)
    deduction_date = fields.Date("Deduction Date", tracking=True, required=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee", required=True, tracking=True)
    amount = fields.Float(string="Amount", tracking=True, required=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    journal_id = fields.Many2one('account.journal', string='Journal')
    account_id = fields.Many2one('account.account', string='Debit Account', compute='git_account_id_idd')
    account_idd = fields.Many2one('account.account', string='Credit Account', compute='git_account_id_idd')
    reason = fields.Text(string="Reason", tracking=True)
    cl_salary_advance_id = fields.Many2one('hr.payslip', string='')
    journal_entry_id = fields.Many2one('account.move', string='', copy=False, readonly=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", related="employee_id.company_id",
                                 store=True)

    def close(self):
        for rec in self:
            rec.state = "close"

    @api.onchange('employee_id')
    def get_journal(self):
        for rec in self:
            rec.journal_id = self.env['account.journal'].sudo().search(
                [('is_cl_salary_advance', '=', True), ('company_id', '=', rec.employee_id.company_id.id)], limit=1).id
        # return journal

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError("Can not delete")
        return super().unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('cl.salary.advance') or 'New'
        result = super(ClSalaryAdvance, self).create(vals)
        return result

    @api.depends('journal_id')
    def git_account_id_idd(self):
        for rec in self:
            rec.account_id = False
            rec.account_idd = False
            if rec.journal_id.account_ids and rec.journal_id.account_idd:
                rec.account_id = rec.journal_id.account_ids.id
                rec.account_idd = rec.journal_id.account_idd.id
            else:
                rec.account_id = False
                rec.account_idd = False

    def validate_action(self):
        for rec in self:
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'entry',
                'date': rec.deduction_date,
                'partner_field_mandatory': False,
                'cl_salary_advance_id': rec.id,
                'ref': rec.name,
                'journal_id': rec.journal_id.id,
                'line_ids': [(0, 0, {
                    'account_id': rec.account_id.id,
                    'name': rec.employee_id.name,
                    'partner_id': rec.employee_id.address_home_id.id,
                    'debit': rec.amount,
                }), (0, 0, {
                    'account_id': rec.account_idd.id,
                    'name': rec.employee_id.name,
                    'credit': rec.amount,
                })],
            })
            rec.journal_entry_id = invoice.id
            rec.state = 'validate'

    def confirm_action(self):
        for rec in self:
            rec.state = 'confirmed'


class HrPaysLipInherit(models.Model):
    _inherit = 'hr.payslip'

    loans_line_ids = fields.One2many(comodel_name="loans.line", inverse_name="loans_payslip_id", string="",
                                     required=False,
                                     compute='get_loan_ids')
    loans = fields.Float(string="Loans", compute='get_total_loans')
    salary_advance_ids = fields.One2many(comodel_name="salary.advance", inverse_name="salary_advance_id", string="",
                                         required=False, compute='get_salary_advance_ids')
    cl_salary_advance_ids = fields.One2many(comodel_name="cl.salary.advance", inverse_name="cl_salary_advance_id",
                                            string="",
                                            required=False, compute='cl_get_salary_advance_ids')
    salary_advance = fields.Float(string="Salary Advance", compute='get_total_salary_advance')
    cl_salary_advance = fields.Float(string="Salary Advance")
    car_loans = fields.Float(string="Car Loans", required=False, )
    other_loans = fields.Float(string="Other Loans", required=False, )

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_loan_ids(self):
        self.loans_line_ids = False
        loans = self.env['loans'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'confirmed'),
            ('loans_ids', '!=', False),
        ])
        list = []
        if loans:
            for loan in loans.loans_ids:
                if loan.name >= self.date_from and loan.name <= self.date_to:
                    list.append(loan.id)
            self.loans_line_ids = list
        else:
            self.loans_line_ids = False

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_total_loans(self):
        loan_loan = 0
        for rec in self:
            rec.loans = False
            if rec.loans_line_ids:
                for line in rec.loans_line_ids:
                    loan_loan = loan_loan + line.amount
                rec.loans = loan_loan
            else:
                rec.loans = False

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_salary_advance_ids(self):
        self.salary_advance_ids = False
        salary_advance = self.env['salary.advance'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'confirmed'),
            ('deduction_date', '<=', self.date_to),
            ('deduction_date', '>=', self.date_from),
        ])
        if salary_advance:
            for rec in self:
                rec.salary_advance_ids = salary_advance
        else:
            self.salary_advance_ids = False

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_total_salary_advance(self):
        advance = 0
        for rec in self:
            rec.salary_advance = False
            if rec.salary_advance_ids:
                for line in rec.salary_advance_ids:
                    advance = advance + line.amount
                rec.salary_advance = advance
            else:
                rec.salary_advance = False

    @api.depends('employee_id', 'date_from', 'date_to', )
    def cl_get_salary_advance_ids(self):
        for rec in self:
            rec.salary_advance_ids = False
            salary_advance = self.env['cl.salary.advance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'confirmed'),
                ('deduction_date', '<=', rec.date_to),
                ('deduction_date', '>=', rec.date_from),
            ])
            if salary_advance:
                rec.cl_salary_advance_ids = salary_advance
                rec.cl_salary_advance = sum(rec.cl_salary_advance_ids.mapped('amount'))
            else:
                rec.cl_salary_advance_ids = False


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    is_loan = fields.Boolean(string="Is Loan", )
    is_salary_advance = fields.Boolean(string="Is Salary Advance", )
    is_cl_salary_advance = fields.Boolean(string="Is Cl", )
    account_ids = fields.Many2one('account.account', string='Debit Account', )
    account_idd = fields.Many2one('account.account', string='Credit Account', )
