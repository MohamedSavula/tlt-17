# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    @api.constrains('work_location_id')
    def limit_employee_work_location(self):
        for rec in self:
            limit_employee = self.search_count(
                [('work_location_id', '=', rec.work_location_id.id)])
            if limit_employee > rec.work_location_id.limit_employee:
                raise UserError(
                    "The number of employees in the work location is full [%s]" % rec.work_location_id.limit_employee)


class HrWorkLocationInherit(models.Model):
    _inherit = 'hr.work.location'

    limit_employee = fields.Integer()
    user_id = fields.Many2many(comodel_name="res.users")
