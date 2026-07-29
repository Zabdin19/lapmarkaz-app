# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Storefront auth built on Frappe's native session handling.

Login itself goes through Frappe's own `/api/method/login`; this module adds
signup, the social-provider list, and the guest-cart handoff that runs on every
new session via hooks.on_session_creation.
"""

import frappe
from frappe.utils import escape_html, validate_email_address
from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys
from frappe.utils.password import get_decrypted_password

from lapmarkaz_app.api.cart import merge_guest_cart_into_user

# Buttons the design asks for, in order.
DESIGNED_PROVIDERS = [
	{"key": "google", "label": "Google", "login_label": "Login with Google"},
	{"key": "facebook", "label": "Facebook", "login_label": "Login with Facebook"},
]


def after_login(login_manager=None):
	"""hooks.on_session_creation — carry an anonymous cart into the account."""
	try:
		merge_guest_cart_into_user()
	except Exception:
		frappe.log_error("Lapmarkaz: guest cart merge failed")


def provider_logins(redirect_to="/"):
	"""Configured Social Login Keys, annotated with what the design expects.

	Providers the design shows but that aren't configured come back with
	`auth_url = None` so the page can say so instead of dead-ending.
	"""
	configured = {}

	for provider in frappe.get_all(
		"Social Login Key",
		filters={"enable_social_login": 1},
		fields=["name", "client_id", "base_url", "provider_name"],
		order_by="name",
	):
		secret = get_decrypted_password(
			"Social Login Key", provider.name, "client_secret", raise_exception=False
		)
		if not (secret and provider.client_id and provider.base_url):
			continue
		if not get_oauth_keys(provider.name):
			continue

		configured[provider.name.lower()] = get_oauth2_authorize_url(provider.name, redirect_to)

	return [
		{**item, "auth_url": configured.get(item["key"])}
		for item in DESIGNED_PROVIDERS
	]


@frappe.whitelist(allow_guest=True, methods=["POST"])
def sign_up(full_name, email, password, phone=None, subscribe=0):
	"""Create a Website User and sign them straight in."""
	email = (email or "").strip().lower()
	full_name = (full_name or "").strip()

	if not full_name:
		frappe.throw("Please tell us your name.")

	validate_email_address(email, throw=True)

	if len(password or "") < 8:
		frappe.throw("Please choose a password of at least 8 characters.")

	if frappe.db.exists("User", email):
		frappe.throw("An account with that email already exists. Try logging in instead.")

	parts = full_name.split(" ", 1)

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": escape_html(parts[0]),
			"last_name": escape_html(parts[1]) if len(parts) > 1 else None,
			"mobile_no": phone,
			"enabled": 1,
			"user_type": "Website User",
			"send_welcome_email": 0,
		}
	)
	user.flags.ignore_permissions = True
	user.flags.no_welcome_mail = True
	user.insert(ignore_permissions=True)

	# Frappe enforces its own password policy here; let it speak for itself.
	user.new_password = password
	user.save(ignore_permissions=True)

	if int(subscribe or 0):
		_subscribe(email, full_name)

	frappe.local.login_manager.login_as(email)
	frappe.db.commit()

	return {"ok": True, "redirect": "/"}


def _subscribe(email, full_name):
	try:
		group = _default_email_group()
		if frappe.db.exists("Email Group Member", {"email": email, "email_group": group}):
			return
		frappe.get_doc(
			{"doctype": "Email Group Member", "email_group": group, "email": email}
		).insert(ignore_permissions=True)
	except Exception:
		frappe.log_error("Lapmarkaz: newsletter subscribe failed")


def _default_email_group():
	name = "Lapmarkaz Newsletter"
	if not frappe.db.exists("Email Group", name):
		frappe.get_doc({"doctype": "Email Group", "title": name}).insert(ignore_permissions=True)
	return name
