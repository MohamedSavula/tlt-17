# -*- coding: utf-8 -*-

from odoo import models, fields


class HrPayrollReportInherit(models.Model):
    _inherit = "hr.payroll.report"

    housing_allowance = fields.Float('Housing Allowance', readonly=True)
    telephone_allowance = fields.Float('Telephone Allowance', readonly=True)
    meal_allowance = fields.Float('Meal Allowance', readonly=True)
    social_insurance = fields.Float('Social Insurance', readonly=True)
    medical_insurance = fields.Float('Medical Insurance', readonly=True)
    c_l = fields.Float('C/L', readonly=True)
    salary_advance = fields.Float('Salary Advance', readonly=True)
    loans = fields.Float('Loans', readonly=True)
    other_deduction = fields.Float('Other Deduction', readonly=True)
    other = fields.Float('Other', readonly=True)
    transportation = fields.Float('Transportation', readonly=True)
    transportation_gouna = fields.Float('Transportation Gouna', readonly=True)
    early_leave = fields.Float('Early Leave', readonly=True)
    late = fields.Float('LATE', readonly=True)
    attendance = fields.Float('Attendance', readonly=True)
    basic_salary_customize = fields.Float(string="Basic Salary Customize", readonly=True)
    s_charge_12 = fields.Float(string="S.Charge 12%", readonly=True)
    annual_increase = fields.Float(string="Annual Increase", readonly=True)

    month_days = fields.Float(string="عدد ايام الشهر", readonly=True)
    compute_sign_out_hours = fields.Float(string="صافي الانصراف المبكر", readonly=True)
    fridays_no = fields.Integer(string="ايام الجمع", readonly=True)
    finger_print_attendance_days = fields.Float(string="ايام الحضور من البصمة", readonly=True)
    casual_leave = fields.Float(string="Day off", readonly=True)
    general_leave = fields.Float(string="Unpaid leave Days", readonly=True)
    rest_allowance = fields.Float(string="Sick leave Days", readonly=True)
    general_leave_amount = fields.Float(string="Unpaid leave Amount", readonly=True)
    rest_allowance_amount = fields.Float(string="Sick leave Amount", readonly=True)
    penalties = fields.Float(string="Penalties", readonly=True)
    vacation = fields.Float(string="Vacation", readonly=True)
    absence_without_permission = fields.Float(string="Absence", readonly=True)
    net_late_hours = fields.Float(string="صافي ساعات التأخير", readonly=True)
    work_location_id = fields.Many2one('hr.work.location', 'Work Location', readonly=True)
    batch_id = fields.Many2one(comodel_name="batch.payslip", string="Batches", readonly=True)

    def _select(self, additional_rules):
        return super()._select(additional_rules) + """,
                        p.compute_sign_out_hours as compute_sign_out_hours,
                        p.month_days as month_days,
                        p.fridays_no as fridays_no,
                        p.batch_id as batch_id,
                        p.vacation as vacation,
                        p.rest_allowance as rest_allowance,
                        p.finger_print_attendance_days as finger_print_attendance_days,
                        p.casual_leave as casual_leave,
                        p.general_leave as general_leave,
                        p.net_late_hours as net_late_hours,
                        p.absence_without_permission as absence_without_permission,
                        c.work_location_id as work_location_id,
                        CASE WHEN wd.id = min_id.min_line THEN plh.total ELSE 0 END as housing_allowance,
                        CASE WHEN wd.id = min_id.min_line THEN plt.total ELSE 0 END as telephone_allowance,
                        CASE WHEN wd.id = min_id.min_line THEN plm.total ELSE 0 END as meal_allowance,
                        CASE WHEN wd.id = min_id.min_line THEN pls.total ELSE 0 END as social_insurance,
                        CASE WHEN wd.id = min_id.min_line THEN ple.total ELSE 0 END as medical_insurance,
                        CASE WHEN wd.id = min_id.min_line THEN plc.total ELSE 0 END as c_l,
                        CASE WHEN wd.id = min_id.min_line THEN pll.total ELSE 0 END as salary_advance,
                        CASE WHEN wd.id = min_id.min_line THEN plo.total ELSE 0 END as loans,
                        CASE WHEN wd.id = min_id.min_line THEN pld.total ELSE 0 END as other_deduction,
                        CASE WHEN wd.id = min_id.min_line THEN plr.total ELSE 0 END as other,
                        CASE WHEN wd.id = min_id.min_line THEN pli.total ELSE 0 END as transportation,
                        CASE WHEN wd.id = min_id.min_line THEN plw.total ELSE 0 END as early_leave,
                        CASE WHEN wd.id = min_id.min_line THEN ply.total ELSE 0 END as late,
                        CASE WHEN wd.id = min_id.min_line THEN plz.total ELSE 0 END as transportation_gouna,
                        CASE WHEN wd.id = min_id.min_line THEN plq.total ELSE 0 END as attendance,
                        CASE WHEN wd.id = min_id.min_line THEN plj.total ELSE 0 END as basic_salary_customize,
                        CASE WHEN wd.id = min_id.min_line THEN plv.total ELSE 0 END as s_charge_12,
                        CASE WHEN wd.id = min_id.min_line THEN plu.total ELSE 0 END as annual_increase,
                        CASE WHEN wd.id = min_id.min_line THEN plp.total ELSE 0 END as general_leave_amount,
                        CASE WHEN wd.id = min_id.min_line THEN pla.total ELSE 0 END as rest_allowance_amount,
                        CASE WHEN wd.id = min_id.min_line THEN plf.total ELSE 0 END as penalties
                        """

    def _from(self, additional_rules):
        from_str = """FROM
            (SELECT * FROM hr_payslip WHERE state IN ('done', 'paid')) p
                left join hr_employee e on (p.employee_id = e.id)
                left join hr_payslip_worked_days wd on (wd.payslip_id = p.id)
                left join hr_work_entry_type wet on (wet.id = wd.work_entry_type_id)
                left join (select payslip_id, min(id) as min_line from hr_payslip_worked_days group by payslip_id) min_id on (min_id.payslip_id = p.id)
                left join hr_payslip_line pln on (pln.slip_id = p.id and (pln.code = 'NET' or pln.code = 'NET_P'))
                left join hr_payslip_line plb on (plb.slip_id = p.id and (plb.code = 'BASIC' or plb.code = 'BASIC_P'))
                left join hr_payslip_line plg on (plg.slip_id = p.id and (plg.code = 'GROSS' or plg.code = 'GROSS_P'))
                left join hr_contract c on (p.contract_id = c.id)
                left join hr_department d on (e.department_id = d.id)
                left join hr_payslip_line plh on (plh.slip_id = p.id and (plh.code = 'HOUS' or plh.code = 'HOUS_P'))
                left join hr_payslip_line plt on (plt.slip_id = p.id and (plt.code = 'TELEPH' or plt.code = 'TELEPH_P'))
                left join hr_payslip_line plm on (plm.slip_id = p.id and (plm.code = 'MEAL' or plm.code = 'MEAL_P'))
                left join hr_payslip_line pls on (pls.slip_id = p.id and (pls.code = 'SINS' or pls.code = 'SINS_P'))
                left join hr_payslip_line ple on (ple.slip_id = p.id and (ple.code = 'MINS' or ple.code = 'MINS_P'))
                left join hr_payslip_line plc on (plc.slip_id = p.id and (plc.code = 'C/L' or plc.code = 'C/L_P'))
                left join hr_payslip_line pll on (pll.slip_id = p.id and (pll.code = 'SAL_ADV' or pll.code = 'SAL_ADV_P'))
                left join hr_payslip_line plo on (plo.slip_id = p.id and (plo.code = 'LOANS' or plo.code = 'LOANS_P'))
                left join hr_payslip_line pld on (pld.slip_id = p.id and (pld.code = 'O_DED' or pld.code = 'O_DED_P'))
                left join hr_payslip_line plr on (plr.slip_id = p.id and (plr.code = 'OTHER' or plr.code = 'OTHER_P'))
                left join hr_payslip_line pli on (pli.slip_id = p.id and (pli.code = 'TRANS' or pli.code = 'TRANS_P'))
                left join hr_payslip_line plw on (plw.slip_id = p.id and (plw.code = 'ELD' or plw.code = 'ELD_P'))
                left join hr_payslip_line ply on (ply.slip_id = p.id and (ply.code = 'LATE' or ply.code = 'LATE_P'))
                left join hr_payslip_line plz on (plz.slip_id = p.id and (plz.code = 'TRANSG' or plz.code = 'TRANSG_P'))
                left join hr_payslip_line plq on (plq.slip_id = p.id and (plq.code = 'ATTD' or plq.code = 'ATTD_P'))
                left join hr_payslip_line plj on (plj.slip_id = p.id and (plj.code = 'BASIC' or plj.code = 'BASIC_P'))
                left join hr_payslip_line plv on (plv.slip_id = p.id and (plv.code = 'SC12' or plv.code = 'SC12_P'))
                left join hr_payslip_line plu on (plu.slip_id = p.id and (plu.code = 'AI' or plu.code = 'AI_P'))
                left join hr_payslip_line plp on (plp.slip_id = p.id and (plp.code = 'UL' or plp.code = 'UL_P'))
                left join hr_payslip_line pla on (pla.slip_id = p.id and (pla.code = 'SL' or pla.code = 'SL_P'))
                left join hr_payslip_line plf on (plf.slip_id = p.id and (plf.code = 'PEN' or plf.code = 'PEN_P'))
                """
        handled_fields = []
        for rule in additional_rules:
            field_name = rule._get_report_field_name()
            if field_name in handled_fields:
                continue
            handled_fields.append(field_name)
            from_str += """
                        left join hr_payslip_line "%s" on ("%s".slip_id = p.id and "%s".code = '%s')""" % (
                field_name, field_name, field_name, rule.code)
        return from_str

    def _group_by(self, additional_rules):
        return super()._group_by(additional_rules) + """,
                plh.total,
                plt.total,
                plm.total,
                pls.total,
                ple.total,
                plc.total,
                pll.total,
                plo.total,
                pld.total,
                plr.total,
                pli.total,
                plw.total,
                ply.total,
                plz.total,
                plq.total,
                plj.total,
                plv.total,
                plu.total,
                plp.total,
                pla.total,
                plf.total,
                p.month_days,
                p.fridays_no,
                p.batch_id,
                p.finger_print_attendance_days,
                p.casual_leave,
                p.general_leave,
                p.rest_allowance,
                p.vacation,
                p.absence_without_permission,
                p.net_late_hours,
                p.compute_sign_out_hours,
                c.work_location_id
                """
