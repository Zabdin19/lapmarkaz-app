# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint


class PrintingMachine(Document):
	def validate(self):
		self.set_slug()
		self.sync_stock_status()

	def set_slug(self):
		if not self.slug:
			self.slug = frappe.scrub(self.machine_name).replace("_", "-")

	def sync_stock_status(self):
		if cint(self.stock_qty) <= 0 and self.stock_status == "In Stock":
			self.stock_status = "Out of Stock"
