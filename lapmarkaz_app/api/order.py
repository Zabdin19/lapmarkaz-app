# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Turns the visitor's cart into a draft ERPNext Sales Order.

Checkout writes a real Sales Order rather than a storefront-only doctype, so
a web order is the same document staff already fulfil, invoice and report on.
It lands as a draft: the shop confirms by phone first (see the timeline on
the confirmation page), and submitting is that confirmation.

Storefront-only data — the address the shopper typed, the payment method they
chose, the guest access token — rides along in the `lm_*` custom fields
installed by `lapmarkaz_app.setup.erpnext_setup`.
"""

from contextlib import contextmanager

import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import add_days, cint, flt, nowdate

from lapmarkaz_app.api.cart import get_cart_doc
from lapmarkaz_app.api.portal import get_customer_for_user, get_or_create_guest_customer
from lapmarkaz_app.utils.items import get_or_create_item

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


# ---------------------------------------------------------------------- ERPNext
# Where a web order is booked. Shop Settings wins when filled in; otherwise it
# is discovered, so a fresh install takes orders before anyone visits the
# settings page.


def selling_company():
	settings = shop_settings()
	if settings.company and frappe.db.exists("Company", settings.company):
		return settings.company

	from lapmarkaz_app.setup.erpnext_setup import default_company

	company = default_company()
	if not company:
		frappe.throw(
			"No Company is set up yet, so orders can't be recorded. "
			"Please contact support.",
			frappe.ValidationError,
		)
	return company


def selling_price_list():
	settings = shop_settings()
	if settings.selling_price_list and frappe.db.exists("Price List", settings.selling_price_list):
		return settings.selling_price_list

	if frappe.db.exists("Price List", "Standard Selling"):
		return "Standard Selling"

	return frappe.db.get_value("Price List", {"selling": 1, "enabled": 1}, "name")


def shipping_account(company):
	settings = shop_settings()
	if settings.shipping_account and frappe.db.get_value(
		"Account", settings.shipping_account, "company"
	) == company:
		return settings.shipping_account

	# Nothing configured — resolve (or create) the conventional one rather than
	# dropping the charge and quietly under-billing the order.
	from lapmarkaz_app.setup.erpnext_setup import ensure_shipping_account

	return ensure_shipping_account(company)


@contextmanager
def _as_administrator():
	"""Build the order as Administrator, then hand the session straight back.

	ERPNext resolves every line through `get_item_details`, which calls
	`Item.check_permission()` against the *session* user — `ignore_permissions`
	on our own insert never reaches it. A shopper has no read on Item and
	shouldn't get one: that permission would expose the entire item master over
	the API to anyone who can load the shop, guests included.

	By this point nothing the request supplied is still in play. The payment
	method has been re-validated against the live DocType, the Customer was
	resolved server-side from the session or the typed email, and the rates
	come from the stored cart. So this widens what *this code* may write, not
	what the caller may ask for.
	"""
	user = frappe.session.user
	frappe.set_user("Administrator")
	try:
		yield
	finally:
		frappe.set_user(user)


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

	# Captured once: the order is built as Administrator further down, so
	# `frappe.session.user` stops being the shopper partway through.
	session_user = frappe.session.user
	is_guest = session_user == "Guest"

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
		customer = get_customer_for_user(session_user)
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
			"user": session_user,
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

	company = selling_company()
	company_currency = frappe.db.get_value("Company", company, "default_currency")
	price_list = selling_price_list()
	price_list_currency = (
		frappe.db.get_value("Price List", price_list, "currency") if price_list else None
	) or company_currency

	if price_list_currency != company_currency:
		frappe.throw(
			f"The selling price list ({price_list}) is priced in {price_list_currency} but "
			f"{company} sells in {company_currency}. Please fix this in Lapmarkaz Shop Settings.",
			frappe.ValidationError,
		)

	delivery_date = add_days(nowdate(), cint(settings.delivery_days) or DELIVERY_DAYS_FALLBACK)
	shopper_name = " ".join(
		p for p in (payload.get("first_name"), payload.get("last_name")) if p
	)

	with _as_administrator():
		order = frappe.new_doc("Sales Order")
		order.update(
			{
				"customer": customer,
				"order_type": "Sales",
				"company": company,
				"transaction_date": nowdate(),
				"delivery_date": delivery_date,
				"currency": company_currency,
				"conversion_rate": 1,
				"selling_price_list": price_list,
				"price_list_currency": price_list_currency,
				"plc_conversion_rate": 1,
				# Rates come from the catalogue the shopper actually saw. Letting a
				# pricing rule re-price at this point would change the total between
				# the cart page and the confirmation page.
				"ignore_pricing_rule": 1,
				"contact_email": payload.get("email"),
				"contact_phone": payload.get("phone"),
				# ---- storefront fields ----
				"lm_web_order": 1,
				"lm_status": "Pending",
				"lm_user": session_user,
				# A guest has no session to prove ownership with later, so the
				# confirmation page checks this instead of `lm_user`. Signed-in
				# orders don't need it — their session already is the proof.
				"lm_access_token": frappe.generate_hash(length=32) if is_guest else None,
				"lm_customer_name": shopper_name,
				"lm_email": payload.get("email"),
				"lm_phone": payload.get("phone"),
				"lm_address": address.name,
				"lm_address_line": address.address_line,
				"lm_city": address.city,
				"lm_postal_code": address.postal_code,
				"lm_country": "Pakistan",
				"lm_payment_method": method.name,
				"lm_payment_method_code": method.method_code,
				"lm_mode_of_payment": method.mode_of_payment,
				"lm_payment_proof": payment_proof,
				"lm_payment_status": "Unpaid",
			}
		)

		for row in cart.items:
			item_code = get_or_create_item(
				"Lapmarkaz Accessory" if row.item_type == "Accessory" else "Laptop",
				row.accessory if row.item_type == "Accessory" else row.laptop,
			)
			order.append(
				"items",
				{
					"item_code": item_code,
					"item_name": row.item_name,
					"description": row.item_name,
					"qty": cint(row.qty),
					# Both, so nothing downstream recomputes `rate` from an empty
					# price list and zeroes the line.
					"price_list_rate": flt(row.rate),
					"rate": flt(row.rate),
					"discount_percentage": 0,
					"delivery_date": delivery_date,
					"lm_item_type": row.item_type,
					"lm_laptop": row.laptop,
					"lm_accessory": row.accessory,
				},
			)

		if flt(cart.discount_amount):
			order.apply_discount_on = "Net Total"
			order.discount_amount = flt(cart.discount_amount)

		# Shipping rides as an "Actual" charge so it lands in `grand_total` the same
		# way any other charge does, instead of being a number only the storefront
		# knows about.
		charge = shipping_charge(payable)
		if charge:
			account = shipping_account(company)
			if not account:
				frappe.throw(
					"No shipping account is configured, so this order can't be totalled. "
					"Please contact support.",
					frappe.ValidationError,
				)
			order.append(
				"taxes",
				{
					"charge_type": "Actual",
					"account_head": account,
					"description": "Shipping",
					"tax_amount": charge,
				},
			)
		order.lm_shipping_charge = charge

		order.flags.ignore_permissions = True
		order.insert(ignore_permissions=True)

	if settings.reduce_stock_on_order:
		_decrement_stock(order)

	cart.db_set("status", "Ordered")

	redirect = f"/order/{order.name}"
	if order.lm_access_token:
		redirect += f"?t={order.lm_access_token}"

	return {"order": order.name, "redirect": redirect}


def storefront_image(row):
	"""Product image for a Sales Order line, from the catalogue record."""
	if row.get("lm_accessory"):
		return frappe.db.get_value("Lapmarkaz Accessory", row.lm_accessory, "image")
	if row.get("lm_laptop"):
		return frappe.db.get_value("Laptop", row.lm_laptop, "thumbnail")
	return row.get("image")


def _decrement_stock(order):
	for row in order.items:
		if not row.get("lm_laptop"):
			continue

		laptop = frappe.get_doc("Laptop", row.lm_laptop)
		remaining = max(cint(laptop.stock_qty) - cint(row.qty), 0)
		laptop.db_set("stock_qty", remaining)
		if remaining == 0:
			laptop.db_set("stock_status", "Out of Stock")
