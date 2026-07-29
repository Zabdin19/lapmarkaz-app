# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Newsletter signup from the home page footer strip."""

import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import validate_email_address

GROUP = "Lapmarkaz Newsletter"


def email_group():
	if not frappe.db.exists("Email Group", GROUP):
		frappe.get_doc({"doctype": "Email Group", "title": GROUP}).insert(ignore_permissions=True)
	return GROUP


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="email", limit=5, seconds=60 * 10)
def subscribe(email):
	email = (email or "").strip().lower()
	validate_email_address(email, throw=True)

	group = email_group()
	settings = frappe.get_cached_doc("Home Page Settings")
	message = settings.newsletter_success_message or "Thanks — you're on the list."

	if frappe.db.exists("Email Group Member", {"email": email, "email_group": group}):
		return {"ok": True, "message": "You're already subscribed."}

	frappe.get_doc(
		{"doctype": "Email Group Member", "email_group": group, "email": email}
	).insert(ignore_permissions=True)

	return {"ok": True, "message": message}
