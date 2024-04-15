# -*- coding: utf-8 -*-

from odoo import models


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    def export_product(self):
        return self.env.ref('report_stock_picking.id_report_stock_picking').report_action(self)


class GeneralLedgerAccount(models.AbstractModel):
    _name = 'report.report_stock_picking.report_stock_picking'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            sheet = workbook.add_worksheet('Stock')
            sheet.set_column('A:A', 40)
            sheet.set_column('B:B', 20)
            sheet.set_column('C:C', 15)
            sheet.set_column('D:D', 20)
            sheet.set_column('E:E', 35)
            format1 = workbook.add_format({'font_size': 13, 'align': 'center'})
            format2 = workbook.add_format({'font_size': 13, 'align': 'center', 'border': 1})
            row = 0
            if obj.picking_type_id.code == 'incoming':
                sheet.write(row, 0, 'Receive From : ', format1)
                sheet.write(row, 1, str(obj.partner_id.name or ""), format1)
            elif obj.picking_type_id.code == 'outgoing':
                sheet.write(row, 0, 'Delivery Address : ', format1)
                sheet.write(row, 1, str(obj.partner_id.name or ""), format1)
                sheet.write(row + 2, 0, 'Source Location : ', format1)
                sheet.write(row + 2, 1, str(obj.location_id.display_name or ""), format1)
            elif obj.picking_type_id.code == 'internal':
                sheet.write(row, 0, 'Contact : ', format1)
                sheet.write(row, 1, str(obj.partner_id.name or ""), format1)
                sheet.write(row + 2, 0, 'Source Location : ', format1)
                sheet.write(row + 2, 1, str(obj.location_id.display_name or ""), format1)
            sheet.write(row, 3, 'Operation Type : ', format1)
            sheet.write(row, 4, str(obj.picking_type_id.display_name or ""), format1)
            if obj.picking_type_id.code != 'outgoing':
                sheet.write(row + 1, 0, 'Destination Location : ', format1)
                sheet.write(row + 1, 1, str(obj.location_dest_id.display_name or ""), format1)
            sheet.write(row + 1, 3, 'Effective Date : ', format1)
            sheet.write(row + 1, 4, str(obj.date_done or ""), format2)
            sheet.write(row + 4, 0, 'Product', format2)
            sheet.write(row + 4, 1, 'Demand', format2)
            sheet.write(row + 4, 2, 'Done', format2)
            sheet.write(row + 4, 3, 'Unit Of Measure', format2)
            sheet.write(row + 4, 4, 'Total Cost', format2)
            row = 4
            for line in obj.move_ids_without_package:
                row += 1
                sheet.write(row, 0, str(line.product_id.name or ""), format2)
                sheet.write(row, 1, line.product_uom_qty or 0, format2)
                sheet.write(row, 2, line.quantity_done or 0, format2)
                sheet.write(row, 3, str(line.product_uom.name) or "", format2)
                sheet.write(row, 4, line.price_subtotal or 0, format2)
