# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api
from datetime import datetime as dt, date, timedelta


class LogCorrelationAttendance(models.Model):
    _inherit = 'hr.attendance'

    attendance_line_id = fields.Many2one(comodel_name="log.correlation", string="", required=False, )


class LogCorrelation(models.Model):
    _name = 'log.correlation'
    _description = 'Log Correlation'

    name = fields.Char()
    modified_date = fields.Date(string="Modified Date", required=False, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name", required=False, )
    date_from = fields.Date(string="Date From", required=False, )
    date_to = fields.Date(string="Date To", required=False, )
    attendance_line_ids = fields.One2many(comodel_name="hr.attendance", inverse_name="attendance_line_id",
                                          string="", required=False, )

    @api.onchange('employee_id', 'date_from', 'date_to')
    def get_attendance_line(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                attendance = self.env['hr.attendance'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                      ('check_in', '>=',
                                                                       dt.combine(rec.date_from, datetime.time.min)),
                                                                      ('check_out', '<=',
                                                                       dt.combine(rec.date_to, datetime.time.max)), ])
                rec.attendance_line_ids = attendance.ids
