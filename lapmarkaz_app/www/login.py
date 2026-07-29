# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Branded login at /login, overriding Frappe's stock login page.

This app is installed after `frappe`, so this module wins the /login route and
Frappe's own www/login.html is never rendered. Only the markup changes:
authentication still posts to Frappe's native `/api/method/login`, so sessions,
password hashing, rate limiting and CSRF are all stock Frappe.

Because Frappe sends unauthenticated Desk traffic to /login, staff hitting
/app land here too. That is intended — they sign in with the same form, and the
login response's `home_page` sends System Users on to /app.

SESSION SCOPE: Frappe keeps exactly one session cookie (`sid`) per browser, so
a System User on /app and a customer on the storefront cannot both be signed in
in the SAME browser — whichever logs in second replaces the first. That is
Frappe's session model, not a bug. To use both at once, use two separate
browsers (or one incognito window), or host the Desk on its own subdomain so
the cookies are scoped separately.
"""

import frappe


def get_context(context):
	context.no_cache = 1
	context.title = "Login | Lapmarkaz"

	redirect_to = frappe.form_dict.get("redirect-to") or "/"

	if frappe.session.user != "Guest":
		frappe.local.flags.redirect_location = redirect_to
		raise frappe.Redirect

	context.redirect_to = redirect_to

	# Set by the registration flow, which deliberately does not sign the user
	# in — they must authenticate with the credentials they just chose.
	context.just_registered = bool(frappe.form_dict.get("registered"))
	context.needs_verification = bool(frappe.form_dict.get("verify"))

	# Set by /update-password, which likewise refuses to sign anyone in off the
	# back of an emailed reset link.
	context.password_updated = bool(frappe.form_dict.get("password_updated"))

	context.page_bg = "min-h-screen bg-white"
	context.header_variant = "none"
	context.footer_variant = "none"

	return context
