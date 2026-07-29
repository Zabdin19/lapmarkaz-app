# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class LapmarkazPaymentMethod(Document):
	def validate(self):
		self.method_code = (self.method_code or "").strip().lower()
		if not self.method_code:
			frappe.throw("Method Code is required")

		if flt(self.max_order_amount) and flt(self.min_order_amount) > flt(self.max_order_amount):
			frappe.throw("Min Order Amount cannot be greater than Max Order Amount")

		self.enforce_single_default()

	def enforce_single_default(self):
		"""Only one method may be the pre-selected default."""
		if not self.is_default:
			return

		others = frappe.get_all(
			"Lapmarkaz Payment Method",
			filters={"is_default": 1, "name": ["!=", self.name]},
			pluck="name",
		)
		for other in others:
			frappe.db.set_value("Lapmarkaz Payment Method", other, "is_default", 0)

	def city_list(self):
		"""Cities this method is restricted to; empty list means everywhere."""
		raw = self.allowed_cities or ""
		return [c.strip() for c in raw.replace(",", "\n").split("\n") if c.strip()]

	def available_for(self, total, city=None):
		"""Whether this method may be offered for a given cart total and city."""
		if not self.is_enabled:
			return False

		total = flt(total)
		if flt(self.min_order_amount) and total < flt(self.min_order_amount):
			return False
		if flt(self.max_order_amount) and total > flt(self.max_order_amount):
			return False

		cities = self.city_list()
		if cities and city and city not in cities:
			return False

		return True
