# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Branded /update-password, overriding Frappe's stock page.

This app is installed after `frappe`, so this module and its template win the
route and Frappe's Bootstrap version never renders. The reset key in the URL is
still Frappe's own — generated and mailed by `User._reset_password()` — we only
change what the visitor sees.

The key is validated here, at render time, so an expired link shows a friendly
explanation instead of a form that only fails once you've typed a password into
it. Submission goes to `lapmarkaz_app.api.password.complete_reset`.
"""

import frappe

from lapmarkaz_app.api.password import reset_key_state

no_cache = 1


def get_context(context):
	context.no_cache = 1
	context.title = "Reset Password | HamzaTraders"

	context.page_bg = "min-h-screen bg-white"
	context.header_variant = "none"
	context.footer_variant = "none"

	key = frappe.form_dict.get("key") or ""
	context.reset_key = key
	context.password_expired = frappe.form_dict.get("password_expired") in ("true", "1", 1, True)

	# How strict the meter should be, straight from the site's own policy.
	context.password_policy = bool(frappe.get_system_settings("enable_password_policy"))
	context.minimum_score = int(frappe.get_system_settings("minimum_password_score") or 2)

	if key:
		state = reset_key_state(key)
		if state["valid"]:
			context.mode = "reset"
		else:
			context.mode = "error"
			context.error_title = "This link has expired"
			context.error_message = (
				f"{state['message']}. Reset links can only be used once, and expire a short "
				"while after they're sent. Request a fresh one and we'll email it right over."
			)
		return context

	# No key. A signed-in user is simply changing their own password.
	if frappe.session.user != "Guest":
		context.mode = "change"
		return context

	context.mode = "error"
	context.error_title = "This link is incomplete"
	context.error_message = (
		"The reset code is missing from this address. It may have been cut short by your "
		"email client — try copying the whole link, or request a new one below."
	)
	return context
