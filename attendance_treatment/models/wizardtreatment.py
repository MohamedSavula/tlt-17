# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta


class WizardTreatment(models.Model):
    _name = 'wizard.treatment'
    _description = 'date wizard treatment'

    name = fields.Char(string="Name")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    is_do_treatment = fields.Boolean(string="", copy=False)

    def get_attendance(self, treatment, employee):
        work_hours = int(self.env['ir.config_parameter'].sudo().get_param('hours_work', ))
        attendance = self.env['hr.attendance'].sudo().search(
            [('employee_id', '=', employee.id),
             ('check_in', '>=', treatment.check_in - relativedelta(hours=work_hours)),
             ('check_in', '<=', treatment.check_in)],
            limit=1)
        return attendance

    def create_attendance(self, treatment, employee):
        self.env['hr.attendance'].create(
            {'employee_id': employee.id, 'check_in': treatment.check_in,
             'machine_ip': treatment.machine_ip,
             'name_machine': treatment.name_machine,
             })

    def do_treatment_2(self):
        for rec in self:
            attendance_employees = self.env['attendance.treatment'].search(
                [('check_in', '>=', rec.date_from), ('check_in', '<=', rec.date_to)])
            employees = set(attendance_employees.mapped('employee_id'))
            for employee in employees:
                attendance_treatment = self.env['attendance.treatment'].search(
                    [('employee_id', '=', employee.id),
                     ('check_in', '>=', dt.combine(rec.date_from, datetime.time.min)),
                     ('check_in', '<=', dt.combine(rec.date_to, datetime.time.max))], order='check_in')
                for treatment in attendance_treatment:
                    attendance = self.get_attendance(treatment, employee)
                    if attendance:
                        attendance.check_out = treatment.check_in
                    else:
                        self.create_attendance(treatment, employee)
