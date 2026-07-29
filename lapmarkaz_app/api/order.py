# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Turns the visitor's cart into a Lapmarkaz Order."""

import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import add_days, cint, flt, nowdate

from lapmarkaz_app.api.cart import get_cart_doc
from lapmarkaz_app.api.portal import get_customer_for_user, get_or_create_guest_customer

DELIVERY_DAYS_FALLBACK = 4

REQUIRED = ("first_name", "phone", "address_line", "city")

PAYMENT_METHOD_FIELDS = [
	"name",
	"method_name",
	"method_code",
	"description",
	"icon",
	"instructions",
	"requires_proof",
	"is_default",
	"min_order_amount",
	"max_order_amount",
	"allowed_cities",
	"mode_of_payment",
	"display_order",
]


def payment_methods(total=0, city=None, include_unavailable=False):
	"""Enabled payment methods, filtered against this cart's total and city.

	`include_unavailable` keeps every enabled method in the list but tags each
	with `available` — the checkout page uses that so the browser can re-filter
	instantly when the shipping city changes, without another round trip.
	"""
	rows = frappe.get_all(
		"Lapmarkaz Payment Method",
		filters={"is_enabled": 1},
		fields=PAYMENT_METHOD_FIELDS,
		order_by="display_order asc, method_name asc",
	)

	out = []
	for row in rows:
		cities = [
			c.strip()
			for c in (row.allowed_cities or "").replace(",", "\n").split("\n")
			if c.strip()
		]
		row["cities"] = cities

		within_amount = True
		if flt(row.min_order_amount) and flt(total) < flt(row.min_order_amount):
			within_amount = False
		if flt(row.max_order_amount) and flt(total) > flt(row.max_order_amount):
			within_amount = False

		in_city = (not cities) or (not city) or (city in cities)
		row["available"] = bool(within_amount and in_city)

		if row["available"] or include_unavailable:
			out.append(row)

	return out


def resolve_payment_method(method_code, total, city):
	"""Validate a submitted method code server-side.

	The browser is never trusted: the code must exist, be enabled, and still
	satisfy the amount and city rules for *this* cart.
	"""
	code = (method_code or "").strip().lower()
	if not code:
		frappe.throw("Please choose a payment method.")

	name = frappe.db.get_value("Lapmarkaz Payment Method", {"method_code": code}, "name")
	if not name:
		frappe.throw(f"Unknown payment method: {code}", frappe.ValidationError)

	method = frappe.get_cached_doc("Lapmarkaz Payment Method", name)

	if not method.is_enabled:
		frappe.throw(f"{method.method_name} is not available right now.", frappe.ValidationError)

	if not method.available_for(total, city):
		frappe.throw(
			f"{method.method_name} is not available for this order.", frappe.ValidationError
		)

	return method


def shop_settings():
	return frappe.get_cached_doc("Lapmarkaz Shop Settings")


def login_required_message():
	return (
		frappe.db.get_single_value("Lapmarkaz Shop Settings", "login_required_message")
		or "Please log in to complete your order."
	)


def guest_blocked():
	"""True when this visitor may not order because they aren't signed in.

	Guest checkout is allowed by default — an order placed as Guest gets its
	own Customer/Contact (see `get_or_create_guest_customer`), never an
	anonymous placeholder. Ticking "Require Login to Place Order" in Lapmarkaz
	Shop Settings closes that off and forces an account, if that's ever wanted.
	"""
	if frappe.session.user != "Guest":
		return False
	return bool(frappe.db.get_single_value("Lapmarkaz Shop Settings", "require_login_to_order"))


def shipping_charge(subtotal):
	settings = shop_settings()
	threshold = flt(settings.free_shipping_over)
	return 0 if flt(subtotal) >= threshold else flt(settings.shipping_charge)


# allow_guest=True: guest checkout is a supported path (see guest_blocked()).
# Rate limited by IP since this now creates records for unauthenticated
# callers — a real customer placing one order a minute never notices; a script
# hammering the endpoint does.
@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=20, seconds=60 * 60)
def place_order(**payload):
	# Convenience redirect happens on the page; this is the real boundary —
	# only reached when Shop Settings actually requires login.
	if guest_blocked():
		frappe.throw(login_required_message(), frappe.PermissionError)

	is_guest = frappe.session.user == "Guest"

	# Every order must belong to a real Customer. Signed-in shoppers resolve to
	# the Customer behind their Contact; there is no placeholder fallback there.
	# Guests get their own Customer/Contact pair, keyed on the email they typed
	# — never silently attached to somebody else's account (see
	# get_or_create_guest_customer).
	if is_guest:
		email = (payload.get("email") or "").strip()
		if not email:
			frappe.throw(
				"Please enter your email address so we can send your receipt and "
				"let you find this order again.",
				frappe.ValidationError,
			)
		customer, _contact = get_or_create_guest_customer(
			email, payload.get("first_name"), payload.get("last_name"), payload.get("phone")
		)
	else:
		customer = get_customer_for_user(frappe.session.user)
		if not customer:
			frappe.throw(
				"We couldn't find a customer account for you. Please contact support before ordering.",
				frappe.ValidationError,
			)

	cart = get_cart_doc(create=False)
	if not cart or not cart.items:
		frappe.throw("Your cart is empty.")

	missing = [f for f in REQUIRED if not (payload.get(f) or "").strip()]
	if missing:
		frappe.throw("Please fill in: " + ", ".join(f.replace("_", " ") for f in missing))

	settings = shop_settings()

	address = frappe.get_doc(
		{
			"doctype": "Lapmarkaz Address",
			"first_name": payload.get("first_name"),
			"last_name": payload.get("last_name"),
			"phone": payload.get("phone"),
			"email": payload.get("email"),
			"address_line": payload.get("address_line"),
			"city": payload.get("city"),
			"postal_code": payload.get("postal_code"),
			"country": "Pakistan",
			"user": frappe.session.user,
		}
	).insert(ignore_permissions=True)

	# Re-validated against the live DocType, not against anything the browser
	# claims. Covers disabled methods, amount caps and city restrictions.
	payable = flt(cart.subtotal) - flt(cart.discount_amount)
	method = resolve_payment_method(
		payload.get("payment_method_code") or payload.get("payment_method"),
		payable,
		payload.get("city"),
	)

	payment_proof = (payload.get("payment_proof") or "").strip() or None
	if method.requires_proof and not payment_proof:
		frappe.throw(
			f"{method.method_name} requires a payment receipt. Please upload one.",
			frappe.ValidationError,
		)

	order = frappe.new_doc("Lapmarkaz Order")
	order.update(
		{
			"customer_name": " ".join(
				p for p in (payload.get("first_name"), payload.get("last_name")) if p
			),
			"email": payload.get("email"),
			"phone": payload.get("phone"),
			"user": frappe.session.user,
			"customer": customer,
			# A guest has no session to prove ownership with later, so the
			# confirmation page checks this instead of `user`. Signed-in orders
			# don't need it — their session already is the proof.
			"access_token": frappe.generate_hash(length=32) if is_guest else None,
			"status": "Pending",
			"address": address.name,
			"address_line": address.address_line,
			"city": address.city,
			"postal_code": address.postal_code,
			"country": "Pakistan",
			"expected_delivery": add_days(
				nowdate(), cint(settings.delivery_days) or DELIVERY_DAYS_FALLBACK
			),
			"payment_method": method.name,
			"payment_method_code": method.method_code,
			"mode_of_payment": method.mode_of_payment,
			"payment_proof": payment_proof,
			"payment_status": "Unpaid",
			"discount_amount": flt(cart.discount_amount),
			"shipping_charge": shipping_charge(flt(cart.subtotal) - flt(cart.discount_amount)),
			"tax_amount": 0,
		}
	)

	for row in cart.items:
		order.append(
			"items",
			{
				"item_type": row.item_type,
				"laptop": row.laptop,
				"accessory": row.accessory,
				"item_name": row.item_name,
				"image": _image_for(row),
				"qty": cint(row.qty),
				"rate": flt(row.rate),
			},
		)

	order.insert(ignore_permissions=True)

	if settings.reduce_stock_on_order:
		_decrement_stock(order)

	cart.db_set("status", "Ordered")

	redirect = f"/order/{order.name}"
	if order.access_token:
		redirect += f"?t={order.access_token}"

	return {"order": order.name, "redirect": redirect}


def _image_for(row):
	if row.item_type == "Accessory" and row.accessory:
		return frappe.db.get_value("Lapmarkaz Accessory", row.accessory, "image")
	if row.laptop:
		return frappe.db.get_value("Laptop", row.laptop, "thumbnail")
	return None


def _decrement_stock(order):
	for row in order.items:
		if not row.laptop:
			continue

		laptop = frappe.get_doc("Laptop", row.laptop)
		remaining = max(cint(laptop.stock_qty) - cint(row.qty), 0)
		laptop.db_set("stock_qty", remaining)
		if remaining == 0:
			laptop.db_set("stock_status", "Out of Stock")
