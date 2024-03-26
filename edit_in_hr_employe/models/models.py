# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EditInHrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = "edit_In_Hr_Employe"

    arabic_name = fields.Char(string="", required=False, )
    emp_code = fields.Char(String="Emp ID")
    outlet_id = fields.Many2one(comodel_name="outlet", string="Outlet", required=False, )
    employee_id = fields.Char(string="Employee_id", required=False, readonly=True)
    health_certificate_date = fields.Date(string="Health Certificate Date")

    @api.model
    def create(self, vals_list):
        res = super(EditInHrEmployee, self).create(vals_list)
        for rec in res:
            rec.employee_id = self.env['ir.sequence'].next_by_code('employee_id_seq')
        return res
