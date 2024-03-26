from odoo import _, api, fields, models


class PurchaseRequestLine(models.Model):
    _name = "penalities"
    _description = "penalities"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    state = fields.Selection([("draft", "Draft"), ("confirmed", "Confirmed")], readonly=True, default="draft",
                             tracking=True)
    name = fields.Text(string="Description", tracking=True)
    date = fields.Date("Date", tracking=True, )
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee", required=True, tracking=True)
    payslip_id = fields.Many2one(comodel_name='hr.payslip', string="payslip_id")
    penality_group = fields.Many2one(comodel_name='penality.group', string="Penality Group")
    sub_penality = fields.Many2one(comodel_name='penality.sub', string="Sub Penality",
                                   domain="[('penality_group', '=', penality_group)]")
    computation = fields.Selection([("day", "Day"), ("amount", "Amount")], string="Computation", tracking=True)
    days = fields.Float(string="Days", tracking=True)
    amount = fields.Float(string="Amount", tracking=True)
    type = fields.Selection([("managerial", "Managerial"), ("financial", "Financial")], string="Deduction Type",
                            required=True, tracking=True)
    reason = fields.Text(string="Reason", tracking=True)
    company_id = fields.Many2one(comodel_name='res.company', string="Company", related='employee_id.company_id')
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    division = fields.Many2one('hr.department', string="Division", )
    job_id = fields.Many2one('hr.job', 'Job Position', related='employee_id.job_id')
    parent_id = fields.Many2one('hr.employee', 'Manager', related='employee_id.parent_id')
    emp_code = fields.Char(String="Emp Code", )

    @api.onchange('days')
    def get_amount_from_contract(self):
        for rec in self:
            wage_contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
                                                            ('state', '=', 'open')], limit=1)
            if wage_contract:
                rec.amount = (wage_contract.net_gross_salary / 30) * rec.days

    def git_confirmed(self):
        self.state = "confirmed"

    def back_to_draft(self):
        for rec in self:
            rec.state = 'draft'


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    penalities_ids = fields.One2many(comodel_name="penalities", inverse_name="payslip_id", compute="get_penalities_ids")
    penality = fields.Float(string="الجزاءات")

    def back_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_penalities_ids(self):
        for rec in self:
            rec.penalities_ids = rec.penalities_ids
            penality = self.env['penalities'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'confirmed'),
                ('date', '<=', rec.date_to),
                ('date', '>=', rec.date_from),
            ])
            if penality:
                rec.penalities_ids = penality
                penalit = 0
                for line in rec.penalities_ids:
                    penalit = penalit + line.amount
                rec.penality = penalit
            else:
                rec.penalities_ids = False


class PenalityGroup(models.Model):
    _name = "penality.group"
    _description = "penalities group"

    name = fields.Char(string="Group Name", required=True)


class SubPenality(models.Model):
    _name = "penality.sub"
    _description = "penalities sub"

    name = fields.Char(string="Sub Penality", required=True)
    penality_group = fields.Many2one(comodel_name='penality.group', string="Penality Group", required=True)
