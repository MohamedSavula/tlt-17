# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import datetime as dt, date
from time import time
import datetime
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError
from dateutil.relativedelta import relativedelta


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    limit_hours = fields.Float()


class NewModule(models.Model):
    _inherit = 'hr.attendance'

    late = fields.Float(string='Late', compute="compute_early_late")
    over_time = fields.Float(string='Over Time', compute="compute_early_late")
    early_sign_in = fields.Float(string='Early Sign In')
    early_leave = fields.Float(string='Early Leave')
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date TO")
    hour_from = fields.Float(string="Hour From", compute="get_sheft")
    hour_to = fields.Float(string="Hour To", compute="get_sheft")
    department_id = fields.Many2one(related="employee_id.department_id", store=True, string="Department")
    limit_hours = fields.Float(related="employee_id.limit_hours")

    @api.depends('employee_id', 'check_in', 'check_out')
    def get_sheft(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                shifts = self.env['employee.shift.line'].search(
                    [('shift_name_id', '=', rec.employee_id.id)], limit=1)
                rec.hour_from = shifts.hour_from
                rec.hour_to = shifts.hour_to
            else:
                rec.hour_from = rec.hour_from
                rec.hour_to = rec.hour_to

    @api.depends('check_in', 'check_out', 'hour_from', 'hour_to')
    def compute_early_late(self):
        for rec in self:
            rec.late = rec.over_time = 0
            if rec.check_in and rec.check_out:
                hours = rec.worked_hours - rec.limit_hours
                if hours > 0:
                    rec.over_time = hours
                else:
                    rec.late = -hours

    def meshmesh(self):
        attendance = self.env['hr.attendance'].sudo().search([])
        for x in attendance:
            x.sudo().compute_early_late()
