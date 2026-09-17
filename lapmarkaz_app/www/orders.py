# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Customer order history at /orders, backed by Sales Order."""

import frappe

from lapmarkaz_app.utils.chrome import storefront_chrome
from lapmarkaz_app.utils.orders import customer_orders


def get_context(context):
	context.no_cache = 1
	context.title = "My Orders | HamzaTraders"

	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/orders"
		raise frappe.Redirect

	context.orders = customer_orders(limit=50)
	context.page_bg = "bg-page"
	context.update(storefront_chrome(active="/orders"))

	return context
