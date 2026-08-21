# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Keep the shopper's tracking timeline in step with the Sales Order.

A Sales Order carries two statuses: ERPNext's own, which moves on submit and
delivery, and `lm_status`, which is what the customer actually sees on their
order page. Left to itself the second one never moves, so a delivered order
still tells its customer "we'll call you to confirm" — the storefront looks
broken while the Desk looks fine.

These hooks tie the customer-facing status to the two moments staff already
act on. Everything between Confirmed and Delivered stays manual: only the shop
knows when a box was packed or handed to a courier.
"""

import frappe

# Statuses we may overwrite automatically. Anything further along was set by a
# human who knows more about the order than this hook does.
ADVANCEABLE = (None, "", "Pending")


def on_submit(doc, method=None):
	"""Submitting is the confirmation call — move the customer past step one."""
	if not doc.get("lm_web_order"):
		return

	if doc.get("lm_status") in ADVANCEABLE:
		doc.db_set("lm_status", "Confirmed", update_modified=False)


def on_cancel(doc, method=None):
	"""Cancelling in the Desk should not leave the customer waiting on a call."""
	if not doc.get("lm_web_order"):
		return

	if doc.get("lm_status") != "Cancelled":
		doc.db_set("lm_status", "Cancelled", update_modified=False)
