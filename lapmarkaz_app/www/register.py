# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Customer registration at /register.

Posts to `lapmarkaz_app.api.portal.register`, which creates the standard
Frappe User (as a Website User with the Customer role) plus the ERPNext
Customer and Contact records that tie a website session to a selling party.
"""

import frappe


def get_context(context):
	context.no_cache = 1
	context.title = "Create your Account | HamzaTraders"

	redirect_to = frappe.form_dict.get("redirect-to") or "/"

	if frappe.session.user != "Guest":
		frappe.local.flags.redirect_location = redirect_to
		raise frappe.Redirect

	context.redirect_to = redirect_to

	context.page_bg = "bg-page"
	context.header_variant = "wordmark"
	context.footer_variant = "bar"
	context.footer_note = "© 2024 HamzaTraders Pakistan. Secure Checkout."

	return context
