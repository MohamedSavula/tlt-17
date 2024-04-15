# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OtherProductCategory(models.Model):
    _name = 'other.product.category'
    _description = 'Other Product Category'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string="Category", required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,
        store=True)
    parent_id = fields.Many2one(comodel_name="other.product.category", string="Parent Category")
    parent_path = fields.Char(index=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    other_product_category_id = fields.Many2one(comodel_name="other.product.category", string="Other Category")


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    other_product_category_id = fields.Many2one(comodel_name="other.product.category", string="Other Category",
                                                related="product_tmpl_id.other_product_category_id", readonly=False)


class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'

    other_product_category_id = fields.Many2one(comodel_name="other.product.category", string="Other Category",
                                                related="product_id.other_product_category_id", store=True)
