# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class LocationHelpdesk(models.Model):
    _name = 'location.helpdesk'
    _description = 'Location Helpdesk'

    name = fields.Char(string="Name", required=True)


class HelpdeskTicketInherit(models.Model):
    _inherit = 'helpdesk.ticket'

    location_id = fields.Many2one(comodel_name="location.helpdesk")

    @api.onchange('stage_id')
    def check_stage_group(self):
        for rec in self:
            if not self.env.user.has_group(
                    'edit_helpdesk_ticket.id_group_stage_helpdesk_ticket') and rec.stage_id.name != 'New' or (
                    rec._origin.stage_id.name and rec._origin.stage_id.name != 'New' and not self.env.user.has_group(
                'edit_helpdesk_ticket.id_group_stage_helpdesk_ticket')):
                raise UserError("You do not have the authority to change the task")
