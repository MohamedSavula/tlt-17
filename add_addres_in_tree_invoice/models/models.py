# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    full_address = fields.Char(string="Address", compute="get_full_address", store=True)
    vat = fields.Char(string="Tax ID", related="partner_id.vat", store=True)

    @api.depends('partner_id', 'partner_id.street', 'partner_id.street2', 'partner_id.city', 'partner_id.state_id',
                 'partner_id.country_id')
    def get_full_address(self):
        for rec in self:
            address_parts = []
            partner = rec.partner_id
            if partner:
                address_parts.append(partner.street or "")
                address_parts.append(partner.street2 or "")
                address_parts.append(partner.city or "")
                address_parts.append(partner.state_id.name or "")
                address_parts.append(partner.country_id.name or "")
            rec.full_address = " ".join(address_parts)
