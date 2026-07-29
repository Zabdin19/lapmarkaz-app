# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

import frappe

from lapmarkaz_app.api.cart import _serialize, get_cart_doc
from lapmarkaz_app.api.order import guest_blocked, payment_methods, shipping_charge


def get_context(context):
	context.no_cache = 1
	context.title = "Checkout | Lapmarkaz"

	# Lapmarkaz Shop Settings can require an account before ordering. The
	# endpoint enforces it too; this just saves guests filling in the form.
	if guest_blocked():
		frappe.local.flags.redirect_location = "/login?redirect-to=/checkout"
		raise frappe.Redirect

	cart = _serialize(get_cart_doc(create=False))
	if not cart["items"]:
		frappe.local.flags.redirect_location = "/cart"
		raise frappe.Redirect

	context.items = cart["items"]
	context.subtotal = cart["subtotal"]
	context.total_qty = cart["total_qty"]
	context.discount_amount = cart.get("discount_amount") or 0
	context.promo_code = cart.get("promo_code")

	payable = context.subtotal - context.discount_amount
	context.shipping_charge = shipping_charge(payable)
	context.grand_total = payable + context.shipping_charge

	# Every enabled method is sent to the page, each tagged with whether it is
	# available for this cart. The template renders only the available ones, and
	# the browser re-filters instantly when the shipping city changes. The order
	# endpoint re-validates the final choice regardless.
	context.payment_methods = payment_methods(
		total=payable, city=None, include_unavailable=True
	)
	context.cities = frappe.get_meta("Lapmarkaz Address").get_field("city").options.split("\n")

	context.steps = [
		{"key": "shipping", "label": "Shipping"},
		{"key": "payment", "label": "Payment"},
		{"key": "review", "label": "Review"},
	]

	context.is_guest = frappe.session.user == "Guest"

	# Pre-fill from the signed-in user's most recent address, if any.
	context.prefill = {}
	if not context.is_guest:
		last = frappe.get_all(
			"Lapmarkaz Address",
			filters={"user": frappe.session.user},
			fields=["first_name", "last_name", "phone", "email", "address_line", "city", "postal_code"],
			order_by="creation desc",
			limit_page_length=1,
		)
		if last:
			context.prefill = last[0]
		context.prefill.setdefault("email", frappe.session.user)

	# ---- shell -------------------------------------------------------------
	context.page_bg = "bg-page"
	context.header_variant = "checkout"
	context.header_note = "Secure Checkout"
	context.footer_variant = "light"
	context.footer_note = "© 2024 Lapmarkaz. Premium Tech for Pakistan."

	return context
