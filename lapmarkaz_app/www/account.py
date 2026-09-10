# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""My Account: profile, order history and saved addresses for the signed-in user."""

import frappe

from lapmarkaz_app.utils.chrome import storefront_chrome
from lapmarkaz_app.utils.orders import customer_orders


def get_context(context):
	context.no_cache = 1

	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/account"
		raise frappe.Redirect

	user = frappe.get_cached_doc("User", frappe.session.user)
	context.account = {
		"email": user.name,
		"full_name": user.full_name or user.first_name or user.name,
		"first_name": user.first_name,
		"phone": user.mobile_no or user.phone,
	}
	context.title = "My Account | hamzatraders"

	context.orders = customer_orders(limit=20)

	context.addresses = frappe.get_all(
		"Lapmarkaz Address",
		filters={"user": frappe.session.user},
		fields=["name", "first_name", "last_name", "phone", "address_line", "city", "postal_code", "country"],
		order_by="creation desc",
		limit_page_length=10,
	)

	context.is_desk_user = user.user_type == "System User"

	context.page_bg = "bg-page"
	context.update(storefront_chrome(active="/account"))

	return context
