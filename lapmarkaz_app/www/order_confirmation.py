# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Order confirmation, served at /order/<order_id> via hooks.website_route_rules.

`order_id` is a Sales Order name. What the shopper sees is driven by the
storefront `lm_*` fields on it, not by the Sales Order's own workflow status
— a draft order awaiting the confirmation call is "Pending" here, which is
what the timeline below is about.
"""

import frappe
from frappe.utils import getdate

from lapmarkaz_app.api.order import storefront_image

TIMELINE = [
	{"key": "verification", "icon": "phone", "title": "Verification Call",
	 "note": "We'll call you to confirm order details."},
	{"key": "packaging", "icon": "box", "title": "Packaging",
	 "note": "Your machine is inspected once more and packed."},
	{"key": "shipment", "icon": "truck", "title": "Shipment",
	 "note": "Handed to our courier with insured delivery."},
]

# Storefront status (`lm_status`) -> how far along that timeline we are.
STATUS_STAGE = {
	"Pending": 0,
	"Confirmed": 1,
	"Packed": 1,
	"Shipped": 2,
	"Delivered": 2,
	"Cancelled": 0,
}


def _ordinal(day):
	if 11 <= day <= 13:
		return f"{day}th"
	return f"{day}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th') }"


def friendly_date(value):
	"""`Tuesday, Oct 24th`, matching the confirmation design."""
	if not value:
		return None
	date = getdate(value)
	return f"{date.strftime('%A')}, {date.strftime('%b')} {_ordinal(date.day)}"


def get_context(context):
	context.no_cache = 1

	order_id = frappe.form_dict.get("order_id")
	if not order_id or not frappe.db.exists("Sales Order", order_id):
		frappe.throw("Order not found", frappe.DoesNotExistError)

	order = frappe.get_doc("Sales Order", order_id)

	if not order.get("lm_web_order"):
		# Raised in the Desk, not on the storefront: it has no shopper-facing
		# address or timeline, and no token anyone could have been given.
		frappe.throw("Order not found", frappe.DoesNotExistError)

	if "System Manager" not in frappe.get_roles():
		if order.lm_user and order.lm_user != "Guest":
			# Belongs to a real account — only that session (or staff) may view it.
			if order.lm_user != frappe.session.user:
				frappe.throw("You are not permitted to view this order", frappe.PermissionError)
		else:
			# Guest order: Sales Order names are sequential and guessable, so
			# `lm_user` alone (always "Guest") proves nothing. The token from the
			# checkout redirect is the only thing that does.
			import hmac

			token = frappe.form_dict.get("t") or ""
			if not order.lm_access_token or not hmac.compare_digest(order.lm_access_token, token):
				frappe.throw("You are not permitted to view this order", frappe.PermissionError)

	context.order = order
	context.title = f"Order {order.name} | Lapmarkaz"

	# Totals, named the way the storefront talks about them rather than the way
	# ERPNext stores them.
	context.totals = {
		"subtotal": order.total,
		"discount_amount": order.discount_amount,
		"shipping_charge": order.get("lm_shipping_charge"),
		"grand_total": order.grand_total,
	}

	# Note: build these locally. `context` is a dict subclass, so `context.items`
	# would resolve to the built-in dict.items method, not our value.
	rows = []
	for row in order.items:
		display = row.item_name
		if row.get("lm_laptop"):
			meta = frappe.db.get_value("Laptop", row.lm_laptop, ["brand", "model"], as_dict=True)
			if meta:
				display = f"{meta.brand} {meta.model}"
		rows.append(
			{
				"display_name": display,
				"qty": row.qty,
				"amount": row.amount,
				"image": storefront_image(row) or "/assets/lapmarkaz_app/images/laptop-silver.svg",
			}
		)
	context.order_items = rows

	context.expected_delivery = friendly_date(order.delivery_date)
	context.address_lines = [
		line
		for line in (
			order.get("lm_customer_name") or order.customer_name,
			order.get("lm_address_line"),
			", ".join(p for p in (order.get("lm_city"), order.get("lm_postal_code")) if p),
			order.get("lm_country"),
		)
		if line
	]

	stage = STATUS_STAGE.get(order.get("lm_status"), 0)
	context.timeline = [
		{**step, "done": i < stage, "active": i == stage} for i, step in enumerate(TIMELINE)
	]

	# ---- shell -------------------------------------------------------------
	context.page_bg = "bg-white"
	context.header_variant = "wordmark"
	context.footer_variant = "legal"
	context.footer_note = "© 2024 Lapmarkaz Pakistan. All rights reserved."
	context.footer_links = [
		{"label": "Privacy Policy", "href": "/privacy"},
		{"label": "Shipping Policy", "href": "/shipping"},
		{"label": "Refund Policy", "href": "/refunds"},
		{"label": "Store Locator", "href": "/stores"},
		{"label": "Contact Us", "href": "/contact"},
	]

	return context
