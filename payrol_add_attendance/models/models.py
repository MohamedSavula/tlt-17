# -*- coding: utf-8 -*-

from odoo import models, fields, api
import random
import datetime
from datetime import datetime, timedelta, date


class EditHrAttendance(models.Model):
    _inherit = 'hr.attendance'

    hr_attend = fields.Many2one(comodel_name="hr.payslip", string="", required=False, )


class EditHrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    amount = fields.Float(digits=(12, 2))
    total = fields.Float(compute='_compute_total', string='Total', help="Total",
                         digits=(12, 2), store=True)


class EditHrPayslip(models.Model):
    _inherit = 'hr.payslip'

    hr_attend_ids = fields.One2many(comodel_name="hr.attendance", inverse_name="hr_attend", string="", required=False,
                                    compute="get_hr_attend_ids")
    shift_name_ids = fields.One2many(comodel_name="employee.shift.line", inverse_name="shift_payroll_id",
                                     string="", required=False, compute="get_hr_attend_ids")
    department_id = fields.Many2one(related="employee_id.department_id", store=True)
    emp_code = fields.Char(related="employee_id.emp_code", store=True)
    work_location_id = fields.Many2one(related="employee_id.work_location_id", store=True)

    # attendence and shift attendance
    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_hr_attend_ids(self):
        for rec in self:
            shift_attend = self.env['hr.employee'].search([
                ('id', '=', rec.employee_id.id),
                ('shift_name_ids', '!=', False),
            ])
            attend = self.env['hr.attendance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_out', '<=', rec.date_to),
                ('check_in', '>=', rec.date_from),
            ])
            if attend:
                rec.hr_attend_ids = attend
            else:
                rec.hr_attend_ids = False
            if shift_attend:
                rec.shift_name_ids = shift_attend.shift_name_ids
            else:
                rec.shift_name_ids = False

    # calculation fields

    rate = fields.Float(string="rate", required=False, readonly=True, default="1.5")
    month_days = fields.Float(string="Month Days")  # Day
    frist_time = fields.Float(string="frist_time", compute="get_days")  # Day
    second_time = fields.Float(string="second_time", compute="get_days")  # Day
    third_time = fields.Float(string="third_time", compute="get_days")  # Day
    fourth_time = fields.Float(string="fourth_time", compute="get_days")  # Day
    fifth_time = fields.Float(string="fifth_time", compute="get_days")  # Day
    attendance_days = fields.Float(string="Attendance Days")  # code=100
    finger_print_attendance_days = fields.Float(string="Finger Attendance Days")
    total_late_hours = fields.Float(string="Total Late Hours", )
    total_sign_out_hours = fields.Float(string="Total SignOut Hours", )
    over_time = fields.Float(string="Over Time")
    absence_without_permission = fields.Float(string="Absence Without Permission")
    total_penalties = fields.Float(string="Total Penalties", required=False, compute="get_days_penalties")
    total_deduction = fields.Float(string="Total Deduction", required=False, compute="get_days_penalties")
    over_days = fields.Float(string="Over Days", )
    compute_late_hours = fields.Float(string="Compute Late Hours", )
    compute_sign_out_hours = fields.Float(string="Compute SignOut Hours", )
    compute_sign_out_hours_free = fields.Float(string="Compute SignOut Hours Free", )
    net_late_hours_free = fields.Float(string="Net Late Hours Free", )
    net_late_hours = fields.Float(string="Net Late Hours", )
    total_late_signout_permission = fields.Float(string="Total Late Signout Permission", )
    permit_4 = fields.Float(string="Permitted 4", default=4)
    diff_4 = fields.Float(stringe="Difference", )
    # اضافي الساعات بنظام الساعة و نصف والساعتين
    hour_15_bonus = fields.Float()
    hour_2_bonus = fields.Float()
    # حساب حافز الانتظام
    a_100 = fields.Float()
    a_300 = fields.Float()

    rest_allowance = fields.Float(string="Rest Allowance")  # code=103
    rest_allowance_tlt = fields.Float(string="Rest Allowance TLT")  # code=103
    hours_mission = fields.Float(string="Hours Mission")  # code=116
    days_errands = fields.Float(string="Days Errands")
    late_permission = fields.Float(string="Late Permission")  # code=105
    early_sign_out = fields.Float(string="Early Sign Out")  # code=106
    casual_leave = fields.Float(string="casual Leave")  # code=109
    vacation = fields.Float(string="Vacation")  # code=109
    general_leave = fields.Float(string="general leave")  # code=110
    paid_leave = fields.Float(string="paid leave")  # code=111
    car_late_permission = fields.Float(string="Car Late Permission")  # code=118
    # freelancing field
    freelancing_days = fields.Float(string="Freelancing Working Days")
    # no of fridays
    fridays_no = fields.Integer(string="Fridays")

    def get_calculation(self):
        for rec in self:
            rec.finger_print_attendance_days = rec.month_days = 0
            casual_leave = 0
            vacation = 0
            general_leave = 0
            rest_allowance = 0
            rest_allowance_tlt = 0
            # paid_leave = 0
            late_permission = 0
            hours_mission = 0
            days_errands = 0
            car_late_permission = 0
            early_sign_out = 0
            if rec.employee_id and rec.date_from and rec.date_to:
                rec.month_days = (rec.date_to - rec.date_from).days + 1
                if rec.month_days > 31:
                    rec.month_days = 31
                rec.finger_print_attendance_days = len(rec.hr_attend_ids.ids)
                time_offs = self.env['hr.leave'].search(
                    [('state', '=', 'validate'), ('employee_id', '=', rec.employee_id.id),
                     ('request_date_to', '<=', self.date_to), ('request_date_from', '>=', self.date_from), ])
                for offe in time_offs:
                    if offe.holiday_status_id.id == self.env.ref('payrol_add_attendance.id_paid_leave').id:
                        casual_leave += offe.number_of_days
                    elif offe.holiday_status_id.id == self.env.ref('payrol_add_attendance.id_casual_leave').id:
                        general_leave += offe.number_of_days
                    elif offe.holiday_status_id.id == self.env.ref('payrol_add_attendance.id_general_leave').id:
                        vacation += offe.number_of_days
                    elif offe.holiday_status_id.id == self.env.ref('payrol_add_attendance.id_rest_allowance_tlt').id:
                        rest_allowance_tlt += offe.number_of_days
                    elif offe.holiday_status_id.id == self.env.ref('payrol_add_attendance.id_rest_allowance').id:
                        rest_allowance += offe.number_of_days
                    elif offe.holiday_status_id.id == self.env.ref('payrol_add_attendance.id_late_permission').id:
                        if offe.request_unit_hours:
                            late_permission += offe.number_of_hours_display
                        else:
                            late_permission += offe.number_of_hours_display
                    elif offe.holiday_status_id.id == self.env.ref('payrol_add_attendance.id_hours_mission').id:
                        if offe.request_unit_hours:
                            hours_mission += offe.number_of_hours_display
                        else:
                            hours_mission += offe.number_of_hours_display
                    elif offe.holiday_status_id.id == self.env.ref('payrol_add_attendance.id_days_errands').id:
                        if offe.request_unit_hours:
                            days_errands += offe.number_of_days
                        else:
                            days_errands += offe.number_of_days
                    elif offe.holiday_status_id.id == self.env.ref('payrol_add_attendance.id_car_late_permission').id:
                        if offe.request_unit_hours:
                            car_late_permission += offe.number_of_hours_display
                        else:
                            car_late_permission += offe.number_of_hours_display
                    elif offe.holiday_status_id.id == self.env.ref('payrol_add_attendance.id_early_sign_out').id:
                        if offe.request_unit_hours:
                            early_sign_out += offe.number_of_hours_display
                        else:
                            early_sign_out += offe.number_of_hours_display
                rec.casual_leave = casual_leave
                rec.vacation = vacation
                rec.general_leave = general_leave
                rec.rest_allowance = rest_allowance
                rec.rest_allowance_tlt = rest_allowance_tlt
                rec.late_permission = late_permission
                rec.hours_mission = hours_mission
                rec.days_errands = days_errands
                rec.car_late_permission = car_late_permission
                rec.early_sign_out = early_sign_out
                rec.absence_without_permission = rec.month_days - rec.finger_print_attendance_days - rec.fridays_no - rec.casual_leave - rec.vacation - rec.general_leave - rec.rest_allowance - rec.days_errands
                rec.over_time = sum(rec.hr_attend_ids.mapped('over_time'))
                late = 0
                early_leave = 0
                for attend in rec.hr_attend_ids:
                    if attend.late > .15:
                        late += attend.late
                    if attend.early_leave >= .15:
                        early_leave += attend.early_leave
                rec.total_late_hours = late
                rec.total_sign_out_hours = early_leave
                late_compute_sign_out_hours = early_leave - rec.early_sign_out
                if late_compute_sign_out_hours >= 0:
                    rec.compute_sign_out_hours = late_compute_sign_out_hours - rec.compute_sign_out_hours_free
                else:
                    rec.compute_sign_out_hours = 0
                late_compute_late_hours = late - rec.late_permission - rec.hours_mission - rec.car_late_permission
                if late_compute_late_hours >= 0:
                    rec.compute_late_hours = late_compute_late_hours
                else:
                    rec.compute_late_hours = 0
                rec.net_late_hours = rec.total_late_hours - rec.late_permission - rec.net_late_hours_free - rec.hours_mission - rec.car_late_permission + rec.early_sign_out - rec.over_time
                rec.net_late_hours = rec.net_late_hours if rec.net_late_hours > 0 else 0
            else:
                rec.absence_without_permission, rec.early_sign_out, rec.car_late_permission, rec.hours_mission, rec.days_errands, rec.late_permission, rec.rest_allowance, rec.rest_allowance_tlt, rec.general_leave, rec.casual_leave, rec.vacation = rec.absence_without_permission, rec.early_sign_out, rec.car_late_permission, rec.hours_mission, rec.late_permission, rec.rest_allowance, rec.rest_allowance_tlt, rec.general_leave, rec.casual_leave, rec.vacation

    def compute_sheet(self):
        for rec in self:
            rec.get_calculation()
        return super(EditHrPayslip, self).compute_sheet()

    @api.depends('absence_without_permission')
    def get_days(self):
        if self.absence_without_permission:
            for rec in self:
                rec.frist_time = 0
                rec.third_time = 0
                rec.second_time = 0
                rec.fourth_time = 0
                rec.fifth_time = 0
                if rec.absence_without_permission >= 2:
                    rec.second_time = .25
                if rec.absence_without_permission >= 3:
                    rec.third_time = .5
                if rec.absence_without_permission >= 4:
                    rec.fourth_time = 1
                if rec.absence_without_permission >= 5:
                    rec.fifth_time = (rec.absence_without_permission - 4) * 2
        else:
            self.frist_time = 0
            self.third_time = 0
            self.second_time = 0
            self.fourth_time = 0
            self.fifth_time = 0

    # get days penalties
    @api.depends('employee_id', 'date_from', 'date_to')
    def get_days_penalties(self):
        for rec in self:
            days_penalties = sum(self.env['penalities'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'confirmed'),
                ('date', '<=', rec.date_to),
                ('date', '>=', rec.date_from),
            ]).mapped('days'))
            rec.total_penalties = days_penalties
            if rec.frist_time or rec.second_time or rec.third_time or rec.fourth_time \
                    or rec.fifth_time or rec.total_penalties or rec.absence_without_permission:
                rec.total_deduction = rec.frist_time + rec.second_time + rec.third_time + rec.fourth_time + \
                                      rec.fifth_time + rec.total_penalties + rec.absence_without_permission
            else:
                rec.total_deduction = False



class EditInHrContract(models.Model):
    _inherit = 'hr.contract'
    _description = "edit_In_hr.contract"

    allow_to_days = fields.Char(string="Allow Days")
    vacation_days = fields.Char(string="Vacation Days")
    unpaid_leave_days = fields.Float(string="Unpaid Leave Days")
    sick_leave_days = fields.Float(string="Sick Leave Days")
    contract_status = fields.Selection(string="Contract Status",
                                       selection=[('new', 'New'), ('running', 'Running'), ('expired', 'Expired'), ],
                                       required=False, )
    is_allow_to_days = fields.Boolean(compute="get_allow_to_days")
    department_id = fields.Many2one('hr.department', string="Department")
    emp_code = fields.Char(related="employee_id.emp_code", store=True)
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")

    @api.depends('employee_id')
    def get_allow_to_days(self):
        for rec in self:
            rec.is_allow_to_days = False
            rec.department_id = rec.employee_id.department_id.id
            rec.vacation_days = rec.employee_id.allocation_used_display

    def update_allow_to_days(self):
        for rec in self:
            rec.allow_to_days = sum(list(self.env['hr.leave.allocation'].sudo().search(
                [('employee_id', '=', rec.employee_id.id), ('date_from', '>=', rec.from_date),
                 ('date_to', '<=', rec.to_date),
                 ('holiday_status_id.active', '=', True),
                 ('state', '=', 'validate')]).mapped('number_of_days')))
            rec.unpaid_leave_days = sum(list(self.env['hr.leave'].sudo().search(
                [('employee_id', '=', rec.employee_id.id), ('date_from', '>=', rec.from_date),
                 ('date_to', '<=', rec.to_date),
                 ('state', '=', 'validate'),
                 ('holiday_status_id', '=', self.env.ref('payrol_add_attendance.id_casual_leave').id),
                 ]).mapped('number_of_days')))
            rec.sick_leave_days = sum(list(self.env['hr.leave'].sudo().search(
                [('employee_id', '=', rec.employee_id.id), ('date_from', '>=', rec.from_date),
                 ('date_to', '<=', rec.to_date),
                 ('state', '=', 'validate'),
                 ('holiday_status_id', '=', self.env.ref('payrol_add_attendance.id_rest_allowance').id),
                 ]).mapped('number_of_days')))
