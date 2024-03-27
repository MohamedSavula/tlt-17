# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    qty_on_hand_location = fields.Float(string="Qty On Hand", compute="get_qty_on_hand_location")

    @api.depends('product_id', 'location_id')
    def get_qty_on_hand_location(self):
        for rec in self:
            rec.qty_on_hand_location = sum(
                self.env['stock.quant']._gather(rec.product_id, rec.location_id).mapped('quantity'))


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    purchase_requisition_id = fields.Many2one(comodel_name="purchase.requisition")
    purchase_template_id = fields.Many2one(comodel_name="purchase.template", string="Purchase Template", readonly=True)
    is_outlet_receive = fields.Boolean(string="Received", tracking=True)

    def button_validate(self):
        for rec in self:
            for line in rec.move_ids_without_package:
                if line.quantity_done >= line.qty_on_hand_location > 0:
                    line.quantity_done = line.qty_on_hand_location
        return super(StockPickingInherit, self).button_validate()

    def open_barcode(self):
        action = self.env['ir.actions.actions']._for_xml_id('stock_barcode.stock_picking_action_kanban')
        action['context'] = {}
        action['domain'] = [('id', '=', self.id)]
        return action


class PurchaseRequisitionInherit(models.Model):
    _inherit = 'purchase.requisition'

    def domain_purchase_template(self):
        templates = self.env['purchase.template'].search([]).filtered(lambda t: self.env.user in t.user_id)
        return [('id', 'in', templates.ids)]

    purchase_template_id = fields.Many2one(comodel_name="purchase.template", string="Purchase Template",
                                           domain=domain_purchase_template)
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Location where the product you want to unbuild is.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Location where you want to send the components resulting from the unbuild order.")
    is_transfer_approve = fields.Boolean()
    transfer_id = fields.Many2one(comodel_name="stock.picking", copy=False)
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True, default=None,
                                      domain="['|',('warehouse_id', '=', False), ('warehouse_id.company_id', '=', company_id)]")
    ordering_date = fields.Date(string="Ordering Date", default=fields.Date.today(), tracking=True)

    @api.onchange('location_id', 'purchase_template_id')
    def get_picking_type_id(self):
        for rec in self:
            rec.picking_type_id = self.env['stock.picking.type'].search(
                [('code', '=', 'internal'), ('default_location_src_id', '=', rec.location_id.id)], limit=1).id

    @api.onchange('purchase_template_id')
    def get_location_id(self):
        for rec in self:
            if rec.purchase_template_id:
                rec.location_id = rec.purchase_template_id.source_location_id

    @api.onchange('purchase_template_id')
    def purchase_template_line(self):
        for rec in self:
            rec.location_dest_id = rec.purchase_template_id.location_dest_id.id
            rec.line_ids = False
            rec.line_ids = [(0, 0, {
                'name': line.name,
                'sequence': line.sequence,
                'display_type': line.display_type,
                'product_id': line.product_id.id,
                'product_description_variants': line.description,
                'product_uom_id': line.product_uom_id.id if line.product_uom_id else line.product_id.uom_id.id,
                'product_qty': line.product_qty,
                'price_unit': line.price_unit,
                'account_analytic_id': line.account_analytic_id.id,
                'analytic_tag_ids': line.analytic_tag_ids.ids,
            }) for line in rec.purchase_template_id.purchase_template_line_ids]

    def show_transfer(self):
        for rec in self:
            domain = self.env['stock.picking'].sudo().search(
                ['|', ('id', '=', rec.transfer_id.id), ('backorder_id', '=', rec.transfer_id.id)])
            return {
                'type': 'ir.actions.act_window',
                'name': 'Transfer',
                'res_model': 'stock.picking',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', domain.ids)],
            }

    def transfer_approve(self):
        for rec in self:
            if not rec.location_id or not rec.location_dest_id:
                raise UserError(_('Must add Source Location and Destination Location'))
            rec.is_transfer_approve = True

    def create_transfer(self):
        for rec in self:
            operation_type = self.env['stock.picking.type'].search(
                [('code', '=', 'internal'), ('default_location_src_id', '=', rec.location_id.id)], limit=1)
            if not operation_type:
                raise UserError(_('not found operation type'))
            rec.transfer_id = self.env['stock.picking'].create({
                'picking_type_id': operation_type.id,
                'user_id': rec.user_id.id,
                'purchase_requisition_id': rec.id,
                'location_id': rec.location_id.id,
                'location_dest_id': rec.location_dest_id.id,
                'purchase_template_id': rec.purchase_template_id.id,
                'move_ids_without_package': [(0, 0, {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'product_uom_qty': line.product_qty,
                    'location_id': rec.location_id.id,
                    'location_dest_id': rec.location_dest_id.id,
                    'analytic_account_id': line.account_analytic_id.id,
                    'analytic_tag_ids': line.analytic_tag_ids.ids,
                }) for line in rec.line_ids if line.product_qty > 0],
            }).id

    def create_po_tlt(self):
        for rec in self:
            return self.env['purchase.order'].sudo().create({
                'partner_id': rec.vendor_id.id,
                'picking_type_id': self.env['stock.picking.type'].sudo().search(
                    [('warehouse_id', '=', rec.location_dest_id.warehouse_id.id),
                     ('default_location_dest_id', '=', rec.location_dest_id.id)], limit=1).id or 241,
                'requisition_id': rec.id,
            })

    def action_in_progress(self):
        res = super().action_in_progress()
        for rec in self:
            if rec.purchase_template_id.is_send_email:
                po = rec.create_po_tlt()
                po._onchange_requisition_id()
                if not len(po.order_line):
                    po.button_cancel()
                    po.unlink()
                else:
                    ir_model_data = self.env['ir.model.data']
                    try:
                        template_id = ir_model_data._xmlid_lookup('purchase.email_template_edi_purchase')[1]
                    except ValueError:
                        template_id = False
                    ctx = dict(self.env.context or {})
                    ctx.update({
                        'default_model': 'purchase.order',
                        'default_res_ids': po.ids[0],
                        'default_template_id': template_id,
                        'default_composition_mode': 'comment',
                        'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
                        'force_email': True,
                        'mark_rfq_as_sent': True,
                    })
                    vals = {
                        'model': 'purchase.order',
                        'res_ids': po.ids[0],
                        'template_id': template_id,
                        'composition_mode': 'comment',

                    }
                    ctx['model_description'] = _('Request for Quotation')
                    mail_compose_message = self.env['mail.compose.message'].create(vals)
                    mail_compose_message = mail_compose_message.with_context(ctx)
                    mail_compose_message.partner_ids = rec.partner_id.ids
                    mail_compose_message.action_send_mail()
        return res


class PurchaseRequisitionLineInherit(models.Model):
    _inherit = 'purchase.requisition.line'

    name = fields.Char()
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 required=False)


class PurchaseTemplate(models.Model):
    _name = 'purchase.template'
    _description = 'Purchase Template'

    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env['res.company']._company_default_get())
    user_id = fields.Many2many(comodel_name="res.users", string="User Purchase")
    user_email_ids = fields.Many2many(comodel_name="res.users", relation="user_email", column1="user_email1",
                                      column2="user_email2", string="Users Email")
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Location where you want to send the components resulting from the unbuild order.")
    purchase_template_line_ids = fields.One2many(comodel_name="purchase.template.line",
                                                 inverse_name="purchase_template_line_id")
    is_send_email = fields.Boolean(string="Send Email")
    source_location_id = fields.Many2one(comodel_name="stock.location", string="", required=False,
                                         domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")


class PurchaseTemplateLine(models.Model):
    _name = 'purchase.template.line'
    _description = 'Purchase Template Line'

    name = fields.Char()
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Char(string="description")
    purchase_template_line_id = fields.Many2one(comodel_name="purchase.template")
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 required=False)
    categ_id = fields.Many2one(related="product_id.categ_id", store=True, string="Product Category")
    product_uom_id = fields.Many2one(related='product_id.uom_id', store=True)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure')
    product_description_variants = fields.Char('Custom Description')
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    qty_ordered = fields.Float(string='Ordered Quantities')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    schedule_date = fields.Date(string='Scheduled Date')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.onchange('product_id')
    def get_product_uom_id(self):
        for rec in self:
            rec.product_uom_id = rec.product_id.uom_id if rec.product_id else False
