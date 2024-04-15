# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EmployeesApartments(models.Model):
    _name = 'employees.apartments'
    _description = 'Employees Apartments'

    name = fields.Char(string="Name", required=True)
    beds_in_the_room = fields.Integer()
    description = fields.Text()

    @api.depends('name', 'beds_in_the_room')
    def name_get(self):
        res = []
        for record in self:
            name = "%s[%s]" % (record.name, record.beds_in_the_room or "")
            res.append((record.id, name))
        return res


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    apartments_id = fields.Many2one(comodel_name="employees.apartments")
