# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta

from odoo.exceptions import UserError


class TransportationElGonna(models.Model):
    _name = 'transportation.gonna'
    _description = "TransportationElGonna"

    states = fields.Selection([("draft", "Draft"), ("confirmed", "Confirmed")], readonly=True,
                              default="draft", copy=False,
                              tracking=True)

    name = fields.Char('', readonly=True, copy=False, default='New', tracking=True)
    date = fields.Date("Date", tracking=True, required=True)
    payment_date = fields.Date("Payment Date", tracking=True, required=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee", required=True, tracking=True)
    amount = fields.Float(string="Amount", tracking=True, required=True)
    reason = fields.Text(string="", required=False, )
    hr_payslip_id = fields.Many2one(comodel_name="hr.payslip", string="", required=False, )

    def confirm_action(self):
        for rec in self:
            rec.states = 'confirmed'
            rec.name = self.env['ir.sequence'].next_by_code('t_gonna_seq') or 'New'

    def unlink(self):
        for rec in self:
            if rec.states != 'draft':
                raise UserError("Can not delete")
        return super().unlink()


class HrPaysLipInheritNew(models.Model):
    _inherit = 'hr.payslip'

    transportation_el_gonna_ids = fields.One2many(comodel_name="transportation.gonna", inverse_name="hr_payslip_id",
                                                  string="", required=False, compute='get_transportation_el_gonna_ids')

    salary_transportation = fields.Float(string="Salary transportation", compute='get_total_transportation')

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_transportation_el_gonna_ids(self):
        self.transportation_el_gonna_ids = False
        transportation_el_gonna = self.env['transportation.gonna'].search([
            ('employee_id', '=', self.employee_id.id),
            ('states', '=', 'confirmed'),
            ('payment_date', '<=', self.date_to),
            ('payment_date', '>=', self.date_from),
        ])
        if transportation_el_gonna:
            for rec in self:
                rec.transportation_el_gonna_ids = transportation_el_gonna
        else:
            self.transportation_el_gonna_ids = False

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_total_transportation(self):
        for rec in self:
            if rec.transportation_el_gonna_ids:
                rec.salary_transportation = sum(rec.transportation_el_gonna_ids.mapped('amount'))
            else:
                rec.salary_transportation = False
