# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

import frappe

from lapmarkaz_app.api.cart import _serialize, get_cart_doc
from lapmarkaz_app.api.order import guest_blocked, login_required_message


def get_context(context):
	context.no_cache = 1
	context.title = "Your Cart | HamzaTraders"

	cart = _serialize(get_cart_doc(create=False))
	context.cart = cart
	context.items = cart["items"]
	context.subtotal = cart["subtotal"]
	context.total_qty = cart["total_qty"]
	context.discount_amount = cart.get("discount_amount") or 0
	context.promo_code = cart.get("promo_code")
	context.grand_total = context.subtotal - context.discount_amount

	# Surfaced on the checkout button when an account is required to order.
	context.needs_login = guest_blocked()
	context.needs_login_message = login_required_message() if context.needs_login else None

	context.accessories = frappe.get_all(
		"Lapmarkaz Accessory",
		filters={"published": 1},
		fields=["name", "accessory_name", "tagline", "price", "image"],
		order_by="display_order asc",
		limit_page_length=4,
	)

	# ---- shell -------------------------------------------------------------
	context.page_bg = "bg-page"
	context.header_layout = "nav-center"
	context.search_placeholder = "Search products..."
	context.nav_items = [
		{"label": "Laptops", "href": "/shop"},
		{"label": "Accessories", "href": "/accessories"},
		{"label": "Support", "href": "/support"},
	]
	context.trust_strip = [
		{"icon": "check-circle", "label": "Genuine Warranty"},
		{"icon": "truck", "label": "Fast Delivery in PK"},
		{"icon": "lock", "label": "Secure Payment"},
	]

	context.footer_variant = "columns"
	context.footer_blurb = "Premium Tech for Pakistan. Reliable laptops with genuine warranties."
	context.footer_note = "© 2024 HamzaTraders. Premium Tech for Pakistan."
	context.footer_socials = ["instagram", "x", "facebook"]
	context.footer_columns = [
		{
			"links": [
				{"label": "Support Center", "href": "/support"},
				{"label": "Track Order", "href": "/track"},
				{"label": "Returns & Refunds", "href": "/refunds"},
			]
		},
		{
			"links": [
				{"label": "Warranty Policy", "href": "/warranty"},
				{"label": "Shipping Info", "href": "/shipping"},
				{"label": "Privacy", "href": "/privacy"},
				{"label": "Terms of Service", "href": "/terms"},
			]
		},
	]

	return context
