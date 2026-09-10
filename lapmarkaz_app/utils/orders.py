# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""The signed-in shopper's order history.

Web orders are Sales Orders, so the storefront reads them back through the
`lm_*` fields checkout wrote — aliased here to the names the order templates
already use, which keeps ERPNext's vocabulary out of the markup.
"""

import frappe

STATUS_TONES = {
	"Pending": "bg-warning-50 text-warning-700",
	"Confirmed": "bg-brand-50 text-brand-700",
	"Packed": "bg-brand-50 text-brand-700",
	"Shipped": "bg-navy/10 text-navy",
	"Delivered": "bg-success-50 text-success-700",
	"Cancelled": "bg-slate-100 text-slate-500",
}

FIELDS = [
	"name",
	"lm_status as status",
	"transaction_date as order_date",
	"grand_total",
	"total_qty",
	"lm_payment_method as payment_method",
	"lm_payment_status as payment_status",
	"delivery_date as expected_delivery",
]


def customer_orders(user=None, limit=50):
	"""Web orders belonging to `user`, newest first.

	`ignore_permissions` is deliberate: the Customer role has no read on Sales
	Order at all, and granting it would expose more of the document than a
	shopper should see. The filter *is* the permission check — it is pinned to
	the session user, never to anything the request supplied.
	"""
	user = user or frappe.session.user
	if not user or user == "Guest":
		return []

	orders = frappe.get_all(
		"Sales Order",
		filters={"lm_user": user, "lm_web_order": 1},
		fields=FIELDS,
		order_by="creation desc",
		limit_page_length=limit,
		ignore_permissions=True,
	)

	for order in orders:
		order["tone"] = STATUS_TONES.get(order.status, "bg-slate-100 text-slate-500")

	return orders
