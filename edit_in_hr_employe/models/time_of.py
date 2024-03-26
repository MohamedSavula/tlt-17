# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrLeaveInherit(models.Model):
    _inherit = 'hr.leave'

    emp_code = fields.Char(String="Emp ID")

    @api.onchange('emp_code')
    def get_employee_by_code(self):
        for rec in self:
            if len(rec.employee_ids) == 1 and self.env.user.employee_id.id in rec.employee_ids.ids:
                rec.employee_ids = False
            employee = self.env['hr.employee'].sudo().search([('emp_code', '=', rec.emp_code)], limit=1)
            rec.employee_ids = [(4, employee.id)]
