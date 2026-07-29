# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Customer order history at /orders."""

import frappe

from lapmarkaz_app.utils.chrome import storefront_chrome

STATUS_TONES = {
	"Pending": "bg-amber-50 text-amber-700",
	"Confirmed": "bg-sky-50 text-sky-700",
	"Packed": "bg-sky-50 text-sky-700",
	"Shipped": "bg-indigo-50 text-indigo-700",
	"Delivered": "bg-emerald-50 text-emerald-700",
	"Cancelled": "bg-slate-100 text-slate-500",
}


def get_context(context):
	context.no_cache = 1
	context.title = "My Orders | Lapmarkaz"

	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/orders"
		raise frappe.Redirect

	orders = frappe.get_all(
		"Lapmarkaz Order",
		filters={"user": frappe.session.user},
		fields=[
			"name", "status", "order_date", "grand_total", "total_qty",
			"payment_method", "payment_status", "expected_delivery",
		],
		order_by="creation desc",
		limit_page_length=50,
	)
	for order in orders:
		order["tone"] = STATUS_TONES.get(order.status, "bg-slate-100 text-slate-500")

	context.orders = orders
	context.page_bg = "bg-page"
	context.update(storefront_chrome(active="/orders"))

	return context
