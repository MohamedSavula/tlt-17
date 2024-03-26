# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class EditHrEmployee(models.Model):
    _inherit = 'hr.employee'

    batch_id = fields.Many2one(comodel_name="batch.payslip", string="", required=False, )


class EditHrPayslip(models.Model):
    _inherit = 'hr.payslip'

    batch_id = fields.Many2one(comodel_name="batch.payslip", string="", required=False, )


class BatchPayslip(models.Model):
    _name = 'batch.payslip'
    _description = 'New Description'

    name = fields.Char('Batch Name')
    date_from = fields.Date(string="Date From", required=False, )
    date_to = fields.Date(string="Date to", required=False, )
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')

    batch_ids = fields.One2many(comodel_name="hr.employee", inverse_name="batch_id", string="employees", copy=False,
                                required=False)
    payslibs_ids = fields.Many2many(comodel_name="hr.payslip", string="employees", copy=False,
                                    required=False)
    company_id = fields.Many2one('res.company', string='Company', )
    state = fields.Selection(string="", selection=[('draft', 'Draft'), ('wait', 'Waiting'), ('done', 'Done'),
                                                   ('closed', 'Closed')], default='draft', required=False, copy=False)

    @api.onchange('company_id')
    def get_batch_ids(self):
        for rec in self:
            employees = self.env['hr.employee'].sudo().search(
                [('contract_id', '!=', False), ('contract_id.state', '=', 'open'), ('contract_id.state', '=', 'open'),
                 ('company_id', '=', self.company_id.id)])
            rec.batch_ids = employees.ids

    def generate_batches(self):
        for rec in self:
            pay = []
            for line in rec.batch_ids:
                if not line.contract_id.structure_type_id.struct_ids:
                    raise UserError('Must add structure [%s]' % line.display_name)
                payslib = self.env['hr.payslip'].sudo().create({
                    'employee_id': line.id,
                    'date_from': rec.date_from,
                    'date_to': rec.date_to,
                    'contract_id': line.contract_id.id,
                    'struct_id': line.contract_id.structure_type_id.struct_ids[0].id,
                    'batch_id': rec.id,
                    'name': 'Salary Slip - ' + line.name,

                })
                payslib._get_worked_day_lines()
                pay.append(payslib.id)
            rec.payslibs_ids = pay
            rec.state = "wait"

    def comput_sheet(self):
        for rec in self:
            for line in rec.payslibs_ids:
                line._get_worked_day_lines()
                line.get_calculation()
                line.get_penalities_ids()
                line.compute_sheet()
            rec.state = "done"
