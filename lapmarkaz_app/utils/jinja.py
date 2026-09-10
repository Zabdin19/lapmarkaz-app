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


# Single source of truth for "what color role does this condition get" —
# both the solid badge (condition_class, used by shop/laptop cards) and the
# text-only variant (condition_text_class, used by mini_card) are derived
# from this so the two can never disagree again.
CONDITION_BADGE_CLASSES = {
	"New": "bg-brand text-white",
	"Certified Refurbished": "bg-navy/90 text-white",
	"Grade A Refurbished": "bg-success text-white",
	"Grade B Refurbished": "bg-warning text-white",
	"Excellent Condition": "bg-brand-700 text-white",
}
CONDITION_TEXT_CLASSES = {
	"New": "text-brand",
	"Certified Refurbished": "text-navy",
	"Grade A Refurbished": "text-success-700",
	"Grade B Refurbished": "text-warning-700",
	"Excellent Condition": "text-brand-700",
}
DEFAULT_CONDITION_BADGE = "bg-navy/90 text-white"
DEFAULT_CONDITION_TEXT = "text-navy"


def condition_class(condition):
	"""Solid badge colour for a condition, matching the shop listing design."""
	return CONDITION_BADGE_CLASSES.get(condition, DEFAULT_CONDITION_BADGE)


def condition_text_class(condition):
	"""Text-only colour for a condition, used where a solid badge would be
	too heavy (e.g. the compact `mini_card`)."""
	return CONDITION_TEXT_CLASSES.get(condition, DEFAULT_CONDITION_TEXT)


def product_image(item, field="thumbnail"):
	value = item.get(field) if hasattr(item, "get") else getattr(item, field, None)
	return value or PLACEHOLDER
