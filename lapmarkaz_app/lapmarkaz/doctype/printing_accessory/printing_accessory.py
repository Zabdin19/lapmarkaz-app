# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PrintingAccessory(Document):
	def validate(self):
		self.set_slug()

	def set_slug(self):
		if not self.slug:
			self.slug = frappe.scrub(self.accessory_name).replace("_", "-")
