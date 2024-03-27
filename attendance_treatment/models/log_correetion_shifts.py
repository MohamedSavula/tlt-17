# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EditShift(models.Model):
    _inherit = 'employee.shift.line'

    log_correlation = fields.Many2one(comodel_name="log.correlation.shift", string="", required=False, )


class LogCorrelationShift(models.Model):
    _name = 'log.correlation.shift'
    _description = 'Log Correlation Shift'

    name = fields.Char()
    modified_date = fields.Date(string="Modified Date", required=False, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name", required=False, )
    date_from = fields.Date(string="Date From", required=False, )
    date_to = fields.Date(string="Date To", required=False, )
    shift_line_ids = fields.One2many(comodel_name="employee.shift.line", inverse_name="log_correlation", string="",
                                     required=False,)

    @api.onchange('employee_id', 'date_from', 'date_to')
    def get_shift_line(self):
        for rec in self:
            lin = []
            if rec.date_from and rec.date_to:
                if rec.employee_id.shift_name_ids:
                    for line in rec.employee_id.shift_name_ids:
                        if line.date_from >= rec.date_from and line.date_to <= rec.date_to:
                            lin.append(line.id)
                    rec.shift_line_ids = lin

    def update_shift(self):
        for rec in self:
            shift_correlation = []
            shift_employee = []
            if rec.shift_line_ids:
                for line in rec.shift_line_ids:
                    shift_correlation.append(line.id)
                for lines in rec.employee_id.shift_name_ids:
                    shift_employee.append(lines.id)
            shift_employee.extend(shift_correlation)
            rec.employee_id.shift_name_ids = shift_employee
