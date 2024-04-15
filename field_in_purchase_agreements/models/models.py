# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


#
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        self = self.with_company(self.company_id)
        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_company(self.company_id).get_fiscal_position(partner.id)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id,
        self.company_id = requisition.company_id.id
        self.currency_id = requisition.currency_id.id
        if not self.origin or requisition.name not in self.origin.split(', '):
            if self.origin:
                if requisition.name:
                    self.origin = self.origin + ', ' + requisition.name
            else:
                self.origin = requisition.name
        self.notes = requisition.description
        self.date_order = fields.Datetime.now()

        if requisition.type_id.line_copy != 'copy':
            return

        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context(
                lang=partner.lang or self.env.user.lang,
                partner_id=partner.id
            )
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            taxes_ids = fpos.map_tax(
                line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids

            # Compute quantity and price_unit
            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_qty = 0
            product_qty = line.product_qty - line.qty_ordered - line.rfq_qty - line.on_hand
            # Create PO line
            if product_qty > 0:
                order_line_values = line._prepare_purchase_order_line(
                    name=name, product_qty=product_qty, price_unit=price_unit,
                    taxes_ids=taxes_ids)
                order_line_values['product_uom'] = line.product_uom_id.id
                order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines


class PurchaseAgreementAh(models.Model):
    _inherit = 'purchase.requisition'

    internal_location_id = fields.Many2one(comodel_name="stock.location", string="", required=False,
                                           domain="[('usage','=','internal')]")
    total_cost = fields.Float(string="Total Cost", compute="get_total_cost_line", store=True)
    is_received = fields.Boolean(compute="check_closed")

    def check_closed(self):
        for rec in self:
            rec.is_received = False
            if all(p.ship_status for p in rec.purchase_ids) and all(
                    p.product_qty - p.rfq_qty - p.qty_ordered <= 0 for p in rec.line_ids):
                rec.state = 'done'

    @api.depends('line_ids')
    def get_total_cost_line(self):
        for rec in self:
            rec.total_cost = sum(list(rec.line_ids.mapped('total_cost')))

    def action_in_progress(self):
        res = super(PurchaseAgreementAh, self).action_in_progress()
        for rec in self:
            thread_pool = self.env['mail.thread']
            partners = [x.partner_id.id for x in
                        self.env.ref('field_in_purchase_agreements.id_group_validated_agreements').users]
            if partners:
                thread_pool.message_notify(
                    partner_ids=partners,
                    subject=str('Validated Agreements'),
                    body=('Validated Agreements ' + '<a target=_BLANK href="/web?#id=' + str(
                        rec.id) + '&view_type=form&model=purchase.requisition&action=" style="font-weight: bold">' + str(
                        rec.name) + '</a>'' need to validated'),
                    email_from=self.env.user.company_id.email, )

        return res


class InhResPartner(models.Model):
    _inherit = 'res.partner'

    vendor_name_purchase = fields.Boolean(string="", )


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    vendor_id = fields.Many2one(comodel_name="res.partner", string="Vendor", required=False, )


class PurchaseAgreementAhInheritLine(models.Model):
    _inherit = 'purchase.requisition.line'

    vendor_id = fields.Many2one(related="product_id.vendor_id", store=True)
    # picking_type_id = fields.Many2one('stock.picking.type', string='Deliver To', domain="[('code','=','incoming')]",
    #                                   required=True)
    on_hand = fields.Float(string="On Hand", required=False, compute="get_on_hand", store=True)
    cost_product = fields.Float(string="Cost", compute="get_total_cost", store=True)
    total_cost = fields.Float(string="Total Cost", compute="get_total_cost", store=True)
    rfq_qty = fields.Float(string="", compute="get_rfq_qty")

    @api.depends('requisition_id.purchase_ids.state')
    def get_rfq_qty(self):
        line_found = set()
        for line in self:
            total = 0.0
            for po in line.requisition_id.purchase_ids.filtered(
                    lambda purchase_order: purchase_order.state in ['draft', 'sent', 'to approve']):
                for po_line in po.order_line.filtered(lambda order_line: order_line.product_id == line.product_id):
                    if po_line.product_uom != line.product_uom_id:
                        total += po_line.product_uom._compute_quantity(po_line.product_qty, line.product_uom_id)
                    else:
                        total += po_line.product_qty
            if line.product_id not in line_found:
                line.rfq_qty = total
                line_found.add(line.product_id)
            else:
                line.rfq_qty = 0

    @api.depends('product_id', 'product_qty')
    def get_total_cost(self):
        for rec in self:
            rec.cost_product = rec.product_id.standard_price if rec.product_id else 0
            rec.total_cost = rec.cost_product * rec.product_qty

    @api.depends('product_id')
    def get_on_hand(self):
        for rec in self:
            rec.on_hand = sum(
                self.env['stock.quant']._gather(rec.product_id, rec.requisition_id.location_id).mapped('quantity'))
