# -*- coding: utf-8 -*-

from odoo import models, api


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    @api.onchange('company_id')
    def change_company_contract(self):
        for rec in self:
            rec.contract_id.company_id = rec.company_id

    def toggle_active(self):
        res = super(HrEmployeeInherit, self).toggle_active()
        self.env['hr.contract'].sudo().search(
            [('employee_id', '=', self.id)], limit=1).update(
            {'state': 'close', 'active': False})
        return res
