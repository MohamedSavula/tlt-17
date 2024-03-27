# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api
import csv
import binascii
from datetime import timedelta
from io import StringIO
import chardet
from datetime import datetime as time


class UploadSheetAttendance(models.Model):
    _name = 'upload.sheet.attendance'
    _description = 'Upload Sheet Attendance'

    lot_sheet_id = fields.Many2many(comodel_name="ir.attachment")
    machine_ip = fields.Selection(string="Machine Name",
                                  selection=[('one_ninety', 'One ninety'), ('origins', 'Origins'), ('bistro', 'Bistro'),
                                             ('factory', 'Factory'), ('coconut', 'Coconut'),
                                             ('katameya_office', 'Katameya office')], required=True)

    def create_data(self):
        for rec in self:
            for lot_sheet in rec.lot_sheet_id:
                csv_data = binascii.a2b_base64(lot_sheet.datas)
                result = chardet.detect(csv_data)
                encoding = result['encoding']
                csv_text = csv_data.decode(encoding)
                csv_file = StringIO(csv_text)
                csv_reader = csv.reader(csv_file)
                employee = False
                date_format = "%m/%d/%Y %H:%M"
                for row in csv_reader:
                    if row[0] == 'User ID':
                        employee = self.env['hr.employee'].sudo().search([('emp_code', '=', row[1])], limit=1).id
                    elif employee and '/' in row[0] and (row[3] or row[5]):
                        if row[3]:
                            if row[0] + ' ' + row[3] > "10/27/2023 00:00":
                                self.env['attendance.treatment'].sudo().create({
                                    'employee_id': employee,
                                    'name_machine': rec.machine_ip,
                                    'check_in': time.strptime(row[0] + ' ' + row[3], date_format) + timedelta(hours=-2)
                                })
                            else:
                                self.env['attendance.treatment'].sudo().create({
                                    'employee_id': employee,
                                    'name_machine': rec.machine_ip,
                                    'check_in': time.strptime(row[0] + ' ' + row[3], date_format) + timedelta(hours=-3)
                                })
                        if row[5]:
                            if row[0] + ' ' + row[5] > "10/27/2023 00:00":
                                self.env['attendance.treatment'].sudo().create({
                                    'employee_id': employee,
                                    'name_machine': rec.machine_ip,
                                    'check_in': time.strptime(row[0] + ' ' + row[5], date_format) + timedelta(hours=-2)
                                })
                            else:
                                self.env['attendance.treatment'].sudo().create({
                                    'employee_id': employee,
                                    'name_machine': rec.machine_ip,
                                    'check_in': time.strptime(row[0] + ' ' + row[5], date_format) + timedelta(hours=-3)
                                })


class AttendanceTreatment(models.Model):
    _name = 'attendance.treatment'
    _description = 'hr attendance treatment'

    employee_id = fields.Many2one('hr.employee', string="Employee Name")
    check_in = fields.Datetime(string="Check In")
    check_out = fields.Datetime(string="Check Out")
    from_date = fields.Date()
    to_date = fields.Date()
    machine_ip = fields.Char(string="Machine Ip", required=False, )
    name_machine = fields.Char(string='Machine Name', required=False)
    is_treatment = fields.Boolean(string="Is Treatment", )
    active = fields.Boolean(default=True, help="Set active to false to hide the Account Tag without removing it.")

    @api.model
    def create(self, vals_list):
        res = super(AttendanceTreatment, self).create(vals_list)
        res.get_data()
        return res

    def get_data(self):
        for rec in self:
            if rec.check_in:
                rec.from_date = rec.check_in.date()
                rec.to_date = rec.check_in.date()

    @api.constrains('check_in', 'employee_id')
    def check_data(self):
        for rec in self:
            self.search([('id', '!=', rec.id), ('check_in', '=', rec.check_in),
                         ('employee_id', '=', rec.employee_id.id)]).update({
                'active': False
            })


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    machine_ip = fields.Char(string="Machine Ip", required=False, )
    name_machine = fields.Char(string='Machine Name', required=False)

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        return True
