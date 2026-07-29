# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import cint, flt


class LapmarkazOrder(Document):
	def validate(self):
		self.set_totals()

	def set_totals(self):
		for row in self.items:
			row.qty = max(cint(row.qty), 1)
			row.amount = flt(row.rate) * row.qty

		self.total_qty = sum(cint(r.qty) for r in self.items)
		self.subtotal = sum(flt(r.amount) for r in self.items)
		self.grand_total = (
			flt(self.subtotal)
			- flt(self.discount_amount)
			+ flt(self.shipping_charge)
			+ flt(self.tax_amount)
		)
