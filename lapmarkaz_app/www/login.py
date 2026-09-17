# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Branded website login at /login.

This app is installed after `frappe`, so this module wins the /login route and
can decide whether a request should see the storefront login or Frappe's stock
Desk login. Storefront authentication still posts to Frappe's native
`/api/method/login`, so sessions, password hashing, rate limiting and CSRF are
all stock Frappe.

Frappe sends unauthenticated Desk traffic to /login with a `redirect-to=/app...`
query string. Those requests are handed back to Frappe's original login context
and template; customer-facing website links continue to use the branded page.

SESSION SCOPE: Frappe keeps exactly one session cookie (`sid`) per browser, so
a System User on /app and a customer on the storefront cannot both be signed in
in the SAME browser; whichever logs in second replaces the first. That is
Frappe's session model, not a bug. To use both at once, use two separate
browsers (or one incognito window), or host the Desk on its own subdomain so
the cookies are scoped separately.
"""

from urllib.parse import urlparse

import frappe
from frappe.www import login as frappe_login


def _is_desk_redirect(redirect_to):
	"""Return true for redirects that are clearly headed to the Desk."""
	if not redirect_to:
		return False

	path = urlparse(redirect_to).path
	return path == "/app" or path.startswith("/app/")


def get_context(context):
	context.no_cache = 1
	context.title = "Login | HamzaTraders"

	redirect_to = frappe.form_dict.get("redirect-to") or "/"

	if _is_desk_redirect(redirect_to):
		context = frappe_login.get_context(context)
		context.use_frappe_login = True
		return context

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
