# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Small helpers exposed to the storefront templates via hooks.jinja."""

from frappe.utils import flt

PLACEHOLDER = "/assets/lapmarkaz_app/images/laptop-silver.svg"


def rupees(value, prefix="Rs."):
	"""Format a price the way the designs do: `Rs. 48,000` / `Rs 65,000`."""
	return f"{prefix} {flt(value):,.0f}"


def condition_pill(laptop):
	"""`Grade A Condition` when a grade is set, otherwise the raw condition."""
	grade = laptop.get("grade") if hasattr(laptop, "get") else getattr(laptop, "grade", None)
	if grade:
		return f"Grade {grade} Condition"
	return laptop.get("condition") if hasattr(laptop, "get") else getattr(laptop, "condition", "")


CONDITION_CLASSES = {
	"New": "bg-brand text-white",
	"Certified Refurbished": "bg-navy/90 text-white",
	"Grade A Refurbished": "bg-emerald-800 text-white",
	"Grade B Refurbished": "bg-amber-700 text-white",
	"Excellent Condition": "bg-sky-700 text-white",
}


def condition_class(condition):
	"""Badge colour for a condition, matching the shop listing design."""
	return CONDITION_CLASSES.get(condition, "bg-navy/90 text-white")


def product_image(item, field="thumbnail"):
	value = item.get(field) if hasattr(item, "get") else getattr(item, field, None)
	return value or PLACEHOLDER
