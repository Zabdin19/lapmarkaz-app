# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Context injected into every storefront page (hooks.update_website_context)."""

import os

import frappe

from lapmarkaz_app.api.cart import get_cart_count

CSS_PATH = "lapmarkaz_app/public/css/lapmarkaz.css"


def asset_version():
	"""Cache-buster tied to the Tailwind build, so a rebuild is picked up at once."""
	path = frappe.get_app_path("lapmarkaz_app", "public", "css", "lapmarkaz.css")
	try:
		return str(int(os.path.getmtime(path)))
	except OSError:
		return "0"


def update_context(context):
	context.lm_asset_version = asset_version()
	context.cart_count = get_cart_count()

	user = frappe.session.user
	context.lm_user = None if user == "Guest" else user
	context.lm_user_first_name = None

	if context.lm_user:
		# Greet by first name in the header; fall back to the email local part.
		first_name = frappe.db.get_value("User", user, "first_name")
		context.lm_user_first_name = first_name or user.split("@")[0]

	return context
