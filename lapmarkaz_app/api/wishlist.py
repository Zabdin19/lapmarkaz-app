# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Wishlist. Unlike the cart, this requires a signed-in account — there is no
guest wishlist, so every row is owned by a real User from the start."""

import frappe


def _require_login():
	if frappe.session.user == "Guest":
		frappe.throw(
			"Please sign in to use your wishlist.", frappe.PermissionError
		)


def wishlisted_names():
	"""Laptop names the current user has saved. Empty for guests, no error."""
	if frappe.session.user == "Guest":
		return []
	return frappe.get_all(
		"Lapmarkaz Wishlist Item", filters={"user": frappe.session.user}, pluck="laptop"
	)


@frappe.whitelist(allow_guest=True)
def count():
	return {"count": len(wishlisted_names())}


@frappe.whitelist(allow_guest=True)
def list_ids():
	return {"laptops": wishlisted_names()}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def toggle(laptop):
	_require_login()

	existing = frappe.db.get_value(
		"Lapmarkaz Wishlist Item", {"user": frappe.session.user, "laptop": laptop}, "name"
	)

	if existing:
		frappe.delete_doc("Lapmarkaz Wishlist Item", existing, ignore_permissions=True)
		saved = False
	else:
		frappe.get_doc(
			{"doctype": "Lapmarkaz Wishlist Item", "user": frappe.session.user, "laptop": laptop}
		).insert(ignore_permissions=True)
		saved = True

	return {"saved": saved, "count": len(wishlisted_names())}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def remove(laptop):
	_require_login()
	existing = frappe.db.get_value(
		"Lapmarkaz Wishlist Item", {"user": frappe.session.user, "laptop": laptop}, "name"
	)
	if existing:
		frappe.delete_doc("Lapmarkaz Wishlist Item", existing, ignore_permissions=True)
	return {"count": len(wishlisted_names())}
