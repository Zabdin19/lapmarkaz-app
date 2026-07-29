# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Password reset, layered on top of Frappe's native reset-key flow.

Nothing here invents a token scheme. `frappe.core.doctype.user.user` owns the
reset key — generating it, storing only its SHA-256, expiring it against
System Settings' `reset_password_link_expiry_duration`, and burning it on use.
This module is a thin branded front door onto that machinery:

    request_reset   -> frappe's `reset_password`, plus a per-email rate limit
    reset_key_state -> frappe's `_get_user_for_update_password`, for rendering
    complete_reset  -> frappe's `update_password`, with the auto-login undone

That last point is the one behaviour we deliberately change. Frappe's
`update_password` finishes by calling `login_manager.login_as(user)`, which
signs the visitor straight in off the back of an emailed link. We log that
session out again: reading an inbox should prove you may *set* a password, not
hand you a session. The customer types the new password on our login page.
"""

import frappe
from frappe.rate_limiter import rate_limit

# One fixed sentence, whatever actually happened — unknown address, disabled
# account, Administrator, or a real send. Varying the copy (or the status code)
# would turn this endpoint into an account-existence oracle (CWE-204).
GENERIC_SENT_MESSAGE = (
	"If an account exists for that email, we've sent a password reset link. "
	"Please check your inbox."
)

RESET_WINDOW_SECONDS = 15 * 60
RESET_MAX_REQUESTS = 3


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="email", limit=RESET_MAX_REQUESTS, seconds=RESET_WINDOW_SECONDS, ip_based=False)
def request_reset(email):
	"""Send a password reset link, without confirming whether the account exists.

	Rate limited to three requests per email address per fifteen minutes. That
	is keyed on the address rather than the IP so one person cannot mailbomb a
	stranger; Frappe's own hourly per-IP limit on `reset_password` still applies
	underneath and catches the other direction.
	"""
	from frappe.core.doctype.user.user import reset_password as frappe_reset_password

	email = (email or "").strip()
	if not email:
		frappe.throw("Please enter your email address.", frappe.ValidationError)

	# Called purely for its side effects (key generation + mail). It already
	# swallows unknown users, disabled users and SMTP failures internally, so it
	# cannot raise its way into leaking anything.
	frappe_reset_password(user=email)

	# It ends with a msgprint of its own wording; drop it so the browser sees
	# exactly one message — ours.
	frappe.clear_messages()

	return {"ok": True, "message": GENERIC_SENT_MESSAGE}


def reset_key_state(key):
	"""Whether a reset key is still usable, for deciding what to render.

	Deliberately NOT whitelisted. Server-side page rendering only — exposing key
	validation as an endpoint would hand out a probe for guessing keys.
	"""
	from frappe.core.doctype.user.user import _get_user_for_update_password

	if not key:
		return {"valid": False, "message": "This password reset link is incomplete."}

	result = _get_user_for_update_password(key, None)
	if result.get("message"):
		return {"valid": False, "message": result["message"]}

	return {"valid": True, "user": result.get("user")}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=10, seconds=RESET_WINDOW_SECONDS)
def complete_reset(new_password, key=None, old_password=None):
	"""Set a new password, either from a reset link (`key`) or while signed in.

	Frappe's `update_password` does the real work: password-policy scoring, key
	validation, hashing, and clearing other sessions. It answers with a 410 and
	a plain string when the key is spent or expired, and throws when the policy
	rejects the password.
	"""
	from frappe.core.doctype.user.user import update_password as frappe_update_password

	if not key and not old_password:
		frappe.throw(
			"This password reset link is incomplete. Please request a new one.",
			frappe.ValidationError,
		)

	if old_password and frappe.session.user == "Guest":
		frappe.throw("Please log in to change your password.", frappe.PermissionError)

	outcome = frappe_update_password(
		new_password=new_password,
		key=key,
		old_password=old_password,
		logout_all_sessions=1,
	)

	# Expired or already-used key. `update_password` has set the 410 itself.
	if frappe.local.response.get("http_status_code") == 410:
		return {"ok": False, "expired": True, "message": outcome}

	if key:
		# `update_password` just signed this browser in as the account owner.
		# Undo it — a reset link is not a login link. `logout()` deletes the
		# session, clears the cookies and drops us back to Guest.
		frappe.local.login_manager.logout()
		frappe.db.commit()

		return {
			"ok": True,
			"message": "Password updated successfully.",
			"redirect": "/login?password_updated=1",
		}

	# Signed-in change: the customer stays signed in, so leave the session be.
	frappe.db.commit()
	return {
		"ok": True,
		"message": "Password updated successfully.",
		"redirect": "/account",
	}
