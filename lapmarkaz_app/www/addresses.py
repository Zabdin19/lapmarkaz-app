# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Saved delivery addresses at /addresses."""

import frappe

from lapmarkaz_app.api.portal import get_customer_for_user
from lapmarkaz_app.utils.chrome import storefront_chrome


def get_context(context):
	context.no_cache = 1
	context.title = "My Addresses | HamzaTraders"

	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/addresses"
		raise frappe.Redirect

	context.addresses = frappe.get_all(
		"Lapmarkaz Address",
		filters={"user": frappe.session.user},
		fields=[
			"name", "first_name", "last_name", "phone", "email",
			"address_line", "city", "postal_code", "country", "is_default",
		],
		order_by="is_default desc, creation desc",
		limit_page_length=50,
	)

	context.customer = get_customer_for_user()
	context.page_bg = "bg-page"
	context.update(storefront_chrome(active="/addresses"))

	return context
