# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hours_work = fields.Integer(string='Hours Work')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            hours_work=int(self.env['ir.config_parameter'].sudo().get_param('hours_work', )),
        )

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        int(self.env['ir.config_parameter'].sudo().set_param('hours_work', self.hours_work))
