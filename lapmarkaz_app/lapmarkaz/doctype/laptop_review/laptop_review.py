# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LaptopReview(Document):
	def validate(self):
		if not 1 <= (self.rating or 0) <= 5:
			frappe.throw("Rating must be between 1 and 5")

	def on_update(self):
		self.update_laptop_rating()

	def on_trash(self):
		self.update_laptop_rating()

	def update_laptop_rating(self):
		frappe.get_doc("Laptop", self.laptop).refresh_rating()
