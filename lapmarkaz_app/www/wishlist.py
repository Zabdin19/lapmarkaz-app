# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Wishlist. Requires a signed-in account — there is no guest wishlist."""

import frappe

from lapmarkaz_app.api.wishlist import wishlisted_names
from lapmarkaz_app.utils.chrome import storefront_chrome
from lapmarkaz_app.www.shop import CARD_FIELDS


def get_context(context):
	context.no_cache = 1
	context.title = "My Wishlist | hamzatraders"

	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/wishlist"
		raise frappe.Redirect

	names = wishlisted_names()
	context.wishlist_ids = names
	context.laptops = (
		frappe.get_all(
			"Laptop",
			filters={"name": ["in", names], "published": 1},
			fields=CARD_FIELDS,
			order_by="modified desc",
		)
		if names
		else []
	)

	context.page_bg = "bg-page"
	context.update(storefront_chrome(active="/wishlist"))

	return context
