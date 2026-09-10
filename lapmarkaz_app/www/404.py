# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Branded 404, overriding Frappe's stock "There's nothing here" page.

Frappe renders every miss through `NotFoundPage`, which resolves the template
named "404" across installed apps in reverse install order. This app is
installed after `frappe`, so this template wins and mistyped URLs land in the
storefront's own chrome instead of the default Bootstrap theme.
"""

import frappe

from lapmarkaz_app.utils.chrome import storefront_chrome


def get_context(context):
	context.http_status_code = 404
	context.no_cache = 1
	context.title = "Page Not Found | hamzatraders"

	# The path that missed, so we can show it back to the visitor.
	request = getattr(frappe.local, "request", None)
	context.missing_path = (request.path if request else "") or ""

	context.page_bg = "bg-white"

	# The nav reads from Home Page Settings, same as every other storefront page.
	# Wrapped because a 404 must still render even if that lookup fails.
	try:
		context.update(storefront_chrome())
	except Exception:
		context.header_variant = "wordmark"
		context.footer_variant = "bar"

	return context
