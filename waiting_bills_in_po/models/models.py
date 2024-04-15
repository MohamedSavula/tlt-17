# -*- coding: utf-8 -*-

from odoo import models, fields


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    is_waiting_bills = fields.Boolean(string="Waiting Bills")
