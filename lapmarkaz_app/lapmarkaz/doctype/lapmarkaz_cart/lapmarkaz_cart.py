# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt


class LapmarkazCart(Document):
	def validate(self):
		self.price_items()
		self.set_totals()

	def price_items(self):
		"""Rates always come from the catalogue, never from the browser."""
		for row in self.items:
			row.qty = max(cint(row.qty), 1)

			if row.item_type == "Accessory" and row.accessory:
				row.laptop = None
				name, price, _ = _accessory_snapshot(row.accessory)
			elif row.laptop:
				row.accessory = None
				name, price, _ = _laptop_snapshot(row.laptop)
			else:
				frappe.throw("Every cart row needs a Laptop or an Accessory")

			row.item_name = name
			row.rate = price
			row.amount = flt(price) * row.qty

	def set_totals(self):
		self.total_qty = sum(cint(r.qty) for r in self.items)
		self.subtotal = sum(flt(r.amount) for r in self.items)


def _laptop_snapshot(name):
	row = frappe.db.get_value("Laptop", name, ["laptop_name", "price", "thumbnail"], as_dict=True)
	if not row:
		frappe.throw(f"Laptop {name} not found")
	return row.laptop_name, row.price, row.thumbnail


def _accessory_snapshot(name):
	row = frappe.db.get_value(
		"Lapmarkaz Accessory", name, ["accessory_name", "price", "image"], as_dict=True
	)
	if not row:
		frappe.throw(f"Accessory {name} not found")
	return row.accessory_name, row.price, row.image
