# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt


class Laptop(Document):
	def validate(self):
		self.set_slug()
		self.set_derived_specs()
		self.sync_stock_status()

	def set_slug(self):
		if not self.slug:
			self.slug = frappe.scrub(self.laptop_name).replace("_", "-")

	def set_derived_specs(self):
		if not self.tagline:
			spec = " ".join(b for b in (self.processor_family, self.generation) if b)
			parts = [
				p
				for p in (spec, f"{self.ram_gb}GB RAM" if self.ram_gb else None, self.storage)
				if p
			]
			self.tagline = ", ".join(parts)

		if not self.ram_spec and self.ram_gb:
			self.ram_spec = f"{self.ram_gb}GB"

	def sync_stock_status(self):
		if cint(self.stock_qty) <= 0 and self.stock_status == "In Stock":
			self.stock_status = "Out of Stock"

	def refresh_rating(self):
		avg, count = frappe.db.sql(
			"""select avg(rating), count(name) from `tabLaptop Review` where laptop = %s""",
			self.name,
		)[0]
		self.db_set("rating", flt(avg, 1) if avg else 0)
		self.db_set("review_count", cint(count))


def condition_pill(laptop):
	"""Label shown beside the title on the product page, e.g. 'Grade A Condition'.

	Works on a Document or on the plain dict that the website queries return.
	"""
	grade = laptop.get("grade")
	return f"Grade {grade} Condition" if grade else laptop.get("condition")
