# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LapmarkazWishlistItem(Document):
	def validate(self):
		if frappe.db.exists(
			"Lapmarkaz Wishlist Item",
			{"user": self.user, "laptop": self.laptop, "name": ["!=", self.name]},
		):
			frappe.throw("Already in wishlist")
