# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError
from odoo.tools import float_compare, plaintext2html
from markupsafe import Markup


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    batch_payslip_id = fields.Many2one(comodel_name="batch.payslip")


class BatchPayslipInherit(models.Model):
    _inherit = 'batch.payslip'

    entry_ids = fields.Many2many(comodel_name="account.move", relation="batch_entry_ids", column1="batch_entry1",
                                 column2="batch_entry2", copy=False)

    def create_entry(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')
        for rec in self:
            rec.state = 'closed'
            for line in rec.payslibs_ids:
                if line.state not in ['done', 'paid']:
                    raise UserError("You must payslip (%s) done" % line.display_name)
            work_locations = rec.payslibs_ids.work_location_id
            for work_location in work_locations:
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                payslibs_ids = rec.payslibs_ids.filtered(lambda l: l.work_location_id == work_location)
                move_dict = {
                    'narration': '',
                    'ref': work_location.name + '/' + rec.name,
                    'journal_id': payslibs_ids[0].journal_id.id,
                }
                for slip in payslibs_ids:
                    move_dict['narration'] += plaintext2html(slip.number or '' + ' - ' + slip.employee_id.name or '')
                    move_dict['narration'] += Markup('<br/>')
                    slip_lines = slip._prepare_slip_lines(fields.Date.today(), line_ids)
                    line_ids.extend(slip_lines)

                for line_id in line_ids:  # Get the debit and credit sum.
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']
                pal = round(debit_sum - credit_sum, 2)
                if line_ids[-1]['credit']:
                    line_ids[-1]['credit'] = round(line_ids[-1].get('credit') + pal, 2)
                elif line_ids[-1]['debit']:
                    line_ids[-1]['debit'] = round(line_ids[-1].get('debit') - pal, 2)
                debit_sum = 0
                credit_sum = 0
                for line_id in line_ids:  # Get the debit and credit sum.
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']
                # The code below is called if there is an error in the balance between credit and debit sum.
                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    slip._prepare_adjust_line(line_ids, 'credit', debit_sum, credit_sum, fields.Date.today())
                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    slip._prepare_adjust_line(line_ids, 'debit', debit_sum, credit_sum, fields.Date.today())
                # Add accounting lines in the move
                for line in line_ids:
                    line['analytic_account_id'] = work_location.analytic_account_id.id
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                rec.entry_ids = [(4, self.env['hr.payslip']._create_account_move(move_dict).id)]

    def open_entry(self):
        domain = [("id", "in", self.entry_ids.ids)]
        return {
            "name": "Entries",
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "tree,form",
            "domain": domain,
        }


class HrWorkLocationInherit(models.Model):
    _inherit = 'hr.work.location'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        self.compute_sheet()
        return self.write({'state': 'done'})
