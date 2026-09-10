# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Cart read/write endpoints shared by the storefront pages.

A cart belongs to a User once someone is signed in, and to an opaque
`lm_cart` cookie token while they are browsing as a Guest. Signing in merges
the guest cart into the user's cart.
"""

import frappe
from frappe.utils import cint

COOKIE = "lm_cart"
COOKIE_MAX_AGE = 60 * 60 * 24 * 30


def _cookie_token():
	try:
		return frappe.request.cookies.get(COOKIE)
	except Exception:
		return None


def _set_cookie_token(token):
	# HttpOnly: the cart id is a server-side handle, never read by JavaScript.
	frappe.local.cookie_manager.set_cookie(
		COOKIE, token, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax"
	)


def _clear_cookie_token():
	"""Drop the guest cart cookie once its cart has been merged away."""
	try:
		frappe.local.cookie_manager.delete_cookie(COOKIE)
	except Exception:
		# Not fatal: the guest cart row is gone, so a stale cookie resolves to
		# nothing on the next request.
		pass


def _cart_filters():
	"""Filters that identify the current visitor's active cart, or None."""
	if frappe.session.user != "Guest":
		return {"user": frappe.session.user, "status": "Active"}

	token = _cookie_token()
	if not token:
		return None
	return {"session_id": token, "status": "Active"}


def get_cart_name(create=False):
	filters = _cart_filters()

	if filters:
		name = frappe.db.get_value("Lapmarkaz Cart", filters, "name")
		if name:
			return name

	if not create:
		return None

	cart = frappe.new_doc("Lapmarkaz Cart")
	cart.status = "Active"

	if frappe.session.user != "Guest":
		cart.user = frappe.session.user
	else:
		token = _cookie_token() or frappe.generate_hash(length=32)
		cart.session_id = token
		_set_cookie_token(token)

	cart.insert(ignore_permissions=True)
	return cart.name


def get_cart_doc(create=False):
	name = get_cart_name(create=create)
	return frappe.get_doc("Lapmarkaz Cart", name) if name else None


def get_cart_count():
	"""Total units in the cart. Never creates a cart — safe on every page."""
	name = get_cart_name(create=False)
	if not name:
		return 0
	return cint(frappe.db.get_value("Lapmarkaz Cart", name, "total_qty"))


def _availability(item_type, item):
	"""(available, stock_qty_or_None) for a catalogue item.

	stock_qty is None when the item has no stock tracking, meaning "uncapped".
	"""
	if item_type == "Accessory":
		row = frappe.db.get_value(
			"Lapmarkaz Accessory", item, ["published", "stock_status"], as_dict=True
		)
		if not row or not row.published or row.stock_status == "Out of Stock":
			return False, None
		return True, None

	if item_type == "Printing Accessory":
		row = frappe.db.get_value(
			"Printing Accessory", item, ["published", "stock_status"], as_dict=True
		)
		if not row or not row.published or row.stock_status == "Out of Stock":
			return False, None
		return True, None

	if item_type == "Printing Machine":
		row = frappe.db.get_value(
			"Printing Machine", item, ["published", "stock_status", "stock_qty"], as_dict=True
		)
		if not row or not row.published or row.stock_status == "Out of Stock":
			return False, None
		return True, cint(row.stock_qty)

	row = frappe.db.get_value(
		"Laptop", item, ["published", "stock_status", "stock_qty"], as_dict=True
	)
	if not row or not row.published or row.stock_status == "Out of Stock":
		return False, None
	return True, cint(row.stock_qty)


def merge_guest_cart_into_user():
	"""Fold the anonymous cart into the signed-in customer's cart.

	Runs from hooks.on_session_creation, so it covers login, social login, and
	the first login after registering.

	Rules:
	  * same item in both carts -> quantities are added on one line, never
	    duplicated and never overwritten
	  * merged quantities are capped at available stock
	  * items now unpublished or out of stock are dropped, and reported back
	  * every surviving line is re-priced from the catalogue (Lapmarkaz Cart
	    re-prices on save, so the guest cart's stored rate is never trusted)
	  * the guest cart row is deleted and its cookie cleared

	Idempotent: the guest cart is deleted at the end, so a repeated call finds
	nothing to merge and quantities cannot double.
	"""
	token = _cookie_token()
	if not token or frappe.session.user == "Guest":
		return None

	guest_name = frappe.db.get_value(
		"Lapmarkaz Cart", {"session_id": token, "status": "Active"}, "name"
	)
	if not guest_name:
		return None

	guest = frappe.get_doc("Lapmarkaz Cart", guest_name)
	user_cart = get_cart_doc(create=True)

	if user_cart.name == guest.name:
		# This cart was created anonymously earlier in the same request cycle;
		# just claim it for the user rather than merging it into itself.
		user_cart.db_set("user", frappe.session.user)
		user_cart.db_set("session_id", None)
		_clear_cookie_token()
		return {"claimed": True, "removed": [], "capped": []}

	removed, capped = [], []

	for row in guest.items:
		item = row.laptop or row.accessory or row.printing_machine or row.printing_accessory
		if not item:
			continue

		available, stock_qty = _availability(row.item_type, item)
		if not available:
			removed.append(row.item_name or item)
			continue

		merged = _upsert_row(user_cart, row.item_type, item, row.qty)

		if stock_qty is not None and cint(merged.qty) > stock_qty:
			if stock_qty <= 0:
				user_cart.remove(merged)
				removed.append(row.item_name or item)
			else:
				merged.qty = stock_qty
				capped.append(row.item_name or item)

	for i, row in enumerate(user_cart.items, start=1):
		row.idx = i

	# save() runs Lapmarkaz Cart.price_items(), which re-reads every rate from
	# the catalogue — the guest cart's prices never carry over.
	user_cart.save(ignore_permissions=True)

	# Delete rather than mark abandoned: nothing else references it, and a
	# deleted row makes a second merge a no-op.
	frappe.delete_doc("Lapmarkaz Cart", guest.name, force=1, ignore_permissions=True)
	_clear_cookie_token()

	if removed or capped:
		frappe.cache().set_value(
			f"lm_cart_merge_notice:{frappe.session.user}",
			{"removed": removed, "capped": capped},
			expires_in_sec=300,
		)

	return {"claimed": False, "removed": removed, "capped": capped}


@frappe.whitelist()
def merge_notice():
	"""One-shot notice about anything changed during the last cart merge."""
	key = f"lm_cart_merge_notice:{frappe.session.user}"
	notice = frappe.cache().get_value(key)
	if notice:
		frappe.cache().delete_value(key)
	return notice or {}


ITEM_TYPE_FIELD = {
	"Laptop": "laptop",
	"Accessory": "accessory",
	"Printing Machine": "printing_machine",
	"Printing Accessory": "printing_accessory",
}


def _upsert_row(cart, item_type, item, qty, replace=False):
	field = ITEM_TYPE_FIELD.get(item_type, "laptop")

	for row in cart.items:
		if row.item_type == item_type and row.get(field) == item:
			row.qty = cint(qty) if replace else cint(row.qty) + cint(qty)
			return row

	return cart.append("items", {"item_type": item_type, field: item, "qty": cint(qty) or 1})


def _serialize(cart):
	if not cart:
		return {"items": [], "total_qty": 0, "subtotal": 0}

	items = []
	for row in cart.items:
		if row.item_type == "Accessory":
			meta = frappe.db.get_value(
				"Lapmarkaz Accessory", row.accessory, ["image", "tagline", "slug"], as_dict=True
			) or {}
			items.append(
				{
					"idx": row.idx,
					"name": row.name,
					"item_type": row.item_type,
					"item": row.accessory,
					"item_name": row.item_name,
					"display_name": row.item_name,
					"qty": row.qty,
					"rate": row.rate,
					"amount": row.amount,
					"image": meta.get("image"),
					"tagline": meta.get("tagline"),
					"url": "/accessories",
					"stock_status": "In Stock",
					"condition": None,
				}
			)
		elif row.item_type == "Printing Accessory":
			meta = frappe.db.get_value(
				"Printing Accessory",
				row.printing_accessory,
				["image", "tagline", "slug", "stock_status"],
				as_dict=True,
			) or {}
			items.append(
				{
					"idx": row.idx,
					"name": row.name,
					"item_type": row.item_type,
					"item": row.printing_accessory,
					"item_name": row.item_name,
					"display_name": row.item_name,
					"qty": row.qty,
					"rate": row.rate,
					"amount": row.amount,
					"image": meta.get("image"),
					"tagline": meta.get("tagline"),
					"url": "/printing-accessories/" + (meta.get("slug") or ""),
					"stock_status": meta.get("stock_status"),
					"condition": None,
				}
			)
		elif row.item_type == "Printing Machine":
			meta = frappe.db.get_value(
				"Printing Machine",
				row.printing_machine,
				[
					"thumbnail", "tagline", "slug", "stock_status", "condition",
					"show_condition_badge", "brand", "model",
				],
				as_dict=True,
			) or {}
			items.append(
				{
					"idx": row.idx,
					"name": row.name,
					"item_type": row.item_type,
					"item": row.printing_machine,
					"item_name": row.item_name,
					"display_name": " ".join(
						p for p in (meta.get("brand"), meta.get("model")) if p
					) or row.item_name,
					"qty": row.qty,
					"rate": row.rate,
					"amount": row.amount,
					"image": meta.get("thumbnail"),
					"tagline": meta.get("tagline"),
					"url": "/printing-machines/" + (meta.get("slug") or ""),
					"stock_status": meta.get("stock_status"),
					"condition": meta.get("condition") if meta.get("show_condition_badge", 1) else None,
				}
			)
		else:
			meta = frappe.db.get_value(
				"Laptop",
				row.laptop,
				[
					"thumbnail", "tagline", "slug", "stock_status", "condition",
					"show_condition_badge", "processor", "ram_gb", "storage", "brand", "model",
				],
				as_dict=True,
			) or {}
			specs = " | ".join(
				s
				for s in (
					meta.get("processor"),
					f"{meta.get('ram_gb')}GB RAM" if meta.get("ram_gb") else None,
					meta.get("storage"),
				)
				if s
			)
			items.append(
				{
					"idx": row.idx,
					"name": row.name,
					"item_type": row.item_type,
					"item": row.laptop,
					"item_name": row.item_name,
					# `item_name` is the unique SKU; the storefront shows the
					# clean "<brand> <model>" title instead.
					"display_name": " ".join(
						p for p in (meta.get("brand"), meta.get("model")) if p
					) or row.item_name,
					"qty": row.qty,
					"rate": row.rate,
					"amount": row.amount,
					"image": meta.get("thumbnail"),
					"tagline": specs or meta.get("tagline"),
					"url": "/laptops/" + (meta.get("slug") or ""),
					"stock_status": meta.get("stock_status"),
					"condition": meta.get("condition") if meta.get("show_condition_badge", 1) else None,
				}
			)

	return {
		"name": cart.name,
		"items": items,
		"total_qty": cart.total_qty,
		"subtotal": cart.subtotal,
		"promo_code": cart.promo_code,
		"discount_amount": cart.discount_amount,
	}


# ---------------------------------------------------------------- endpoints


@frappe.whitelist(allow_guest=True)
def count():
	return {"count": get_cart_count()}


@frappe.whitelist(allow_guest=True)
def get():
	return _serialize(get_cart_doc(create=False))


@frappe.whitelist(allow_guest=True, methods=["POST"])
def add(item, item_type="Laptop", qty=1):
	qty = max(cint(qty), 1)
	cart = get_cart_doc(create=True)
	_upsert_row(cart, item_type, item, qty)
	cart.save(ignore_permissions=True)
	return _serialize(cart)


@frappe.whitelist(allow_guest=True, methods=["POST"])
def set_qty(row, qty):
	"""`row` is the Lapmarkaz Cart Item name. qty <= 0 removes the row."""
	cart = get_cart_doc(create=False)
	if not cart:
		return _serialize(None)

	qty = cint(qty)
	cart.items = [r for r in cart.items if r.name != row or qty > 0]
	for r in cart.items:
		if r.name == row:
			r.qty = qty

	for i, r in enumerate(cart.items, start=1):
		r.idx = i

	cart.save(ignore_permissions=True)
	return _serialize(cart)


@frappe.whitelist(allow_guest=True, methods=["POST"])
def remove(row):
	return set_qty(row, 0)


@frappe.whitelist(allow_guest=True, methods=["POST"])
def apply_promo(code):
	"""Percentage promos held in Website Settings-free, code-defined table."""
	promos = {"LAPMARKAZ10": 10, "STUDENT5": 5, "WELCOME15": 15}
	cart = get_cart_doc(create=False)

	if not cart or not cart.items:
		return {"ok": False, "message": "Your cart is empty."}

	pct = promos.get((code or "").strip().upper())
	if not pct:
		return {"ok": False, "message": "That promo code isn't valid."}

	cart.promo_code = code.strip().upper()
	cart.discount_amount = round(cart.subtotal * pct / 100)
	cart.save(ignore_permissions=True)

	return {"ok": True, "message": f"{pct}% off applied.", "cart": _serialize(cart)}
