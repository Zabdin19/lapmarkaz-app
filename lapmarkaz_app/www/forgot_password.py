# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Branded "forgot password" page at /forgot-password.

Frappe has no page at this route — its stock login page hides a reset form
behind a JS toggle — so the "Forgot Password?" link on our login page used to
404. This gives it a real destination.

The form posts to `lapmarkaz_app.api.password.request_reset`, which wraps
Frappe's native `reset_password`. No token handling happens here.
"""

import frappe


def get_context(context):
	context.no_cache = 1
	context.title = "Forgot Password | HamzaTraders"

	# Someone already signed in has no use for this page.
	if frappe.session.user != "Guest":
		frappe.local.flags.redirect_location = "/account"
		raise frappe.Redirect

	context.page_bg = "min-h-screen bg-white"
	context.header_variant = "none"
	context.footer_variant = "none"

	return context
