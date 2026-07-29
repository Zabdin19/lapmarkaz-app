# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Customer portal registration and party linking.

Registration creates the three records ERPNext expects for a self-service
customer, in this order:

    User (Website User + Customer role)
      -> Customer (the selling party)
      -> Contact (links the User to the Customer, carries email + mobile)

The Contact is what ties a logged-in website session to a Customer record, so
anything raised for that party later (Sales Order, Quotation) resolves back to
the right customer without the storefront having to pass it explicitly.

Nothing here grants Desk access: `user_type` stays "Website User", which is
what Frappe's own www/app.py checks before letting anyone into /app.
"""

import frappe
from frappe.utils import cint, escape_html, validate_email_address

CUSTOMER_ROLE = "Customer"
DEFAULT_CUSTOMER_GROUP = "Individual"
DEFAULT_TERRITORY = "Pakistan"
MIN_PASSWORD_LENGTH = 8


def _default_customer_group():
	for name in (DEFAULT_CUSTOMER_GROUP, "All Customer Groups"):
		if frappe.db.exists("Customer Group", name):
			return name
	return frappe.db.get_value("Customer Group", {"is_group": 0}, "name")


def _default_territory():
	for name in (DEFAULT_TERRITORY, "All Territories"):
		if frappe.db.exists("Territory", name):
			return name
	return frappe.db.get_value("Territory", {"is_group": 0}, "name")


def get_customer_for_user(user=None):
	"""The Customer this website user belongs to, via their Contact link."""
	user = user or frappe.session.user
	if not user or user == "Guest":
		return None

	contact = frappe.db.get_value("Contact", {"user": user}, "name")
	if not contact:
		return None

	return frappe.db.get_value(
		"Dynamic Link",
		{"parent": contact, "parenttype": "Contact", "link_doctype": "Customer"},
		"link_name",
	)


def create_customer_and_contact(user_doc, mobile_no=None):
	"""Create the Customer + Contact pair for a freshly registered User.

	Safe to call more than once — if either record already exists for this
	user it is reused rather than duplicated.
	"""
	full_name = user_doc.full_name or user_doc.first_name or user_doc.name

	customer = get_customer_for_user(user_doc.name)
	if not customer:
		customer_doc = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": full_name,
				"customer_type": "Individual",
				"customer_group": _default_customer_group(),
				"territory": _default_territory(),
			}
		)
		customer_doc.flags.ignore_permissions = True
		customer_doc.insert(ignore_permissions=True)
		customer = customer_doc.name

	contact_name = frappe.db.get_value("Contact", {"user": user_doc.name}, "name")
	if not contact_name:
		contact = frappe.get_doc(
			{
				"doctype": "Contact",
				"first_name": user_doc.first_name or full_name,
				"last_name": user_doc.last_name,
				"user": user_doc.name,
				"email_id": user_doc.name,
			}
		)
		contact.append("email_ids", {"email_id": user_doc.name, "is_primary": 1})
		if mobile_no:
			contact.append("phone_nos", {"phone": mobile_no, "is_primary_mobile_no": 1})
		contact.append("links", {"link_doctype": "Customer", "link_name": customer})
		contact.flags.ignore_permissions = True
		contact.insert(ignore_permissions=True)
		contact_name = contact.name

	return customer, contact_name


def get_or_create_guest_customer(email, first_name=None, last_name=None, phone=None):
	"""The Customer for a guest checkout, keyed on email — never on a User.

	Reused across repeat guest orders under the same address IF the matching
	Contact has no `user` (i.e. it was itself created by a previous guest
	order). A Contact that belongs to a registered account is deliberately
	never matched here: an unauthenticated visitor typing someone else's
	email must not get their order silently attached to that person's
	Customer record and surfaced in their "My Orders".
	"""
	email = (email or "").strip().lower()
	full_name = " ".join(p for p in (first_name, last_name) if p) or email or "Guest Customer"

	contact_name = None
	if email:
		# `user` is stored as SQL NULL for guest-created contacts, and NULL
		# never matches an `IN (...)` filter — so this is checked in Python
		# rather than pushed into the query, which would silently match nothing
		# and quietly create a duplicate Customer on every repeat order.
		for row in frappe.get_all(
			"Contact", filters={"email_id": email}, fields=["name", "user"]
		):
			if not row.user:
				contact_name = row.name
				break

	if contact_name:
		customer = frappe.db.get_value(
			"Dynamic Link",
			{"parent": contact_name, "parenttype": "Contact", "link_doctype": "Customer"},
			"link_name",
		)
		if customer:
			return customer, contact_name

	customer_doc = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": full_name,
			"customer_type": "Individual",
			"customer_group": _default_customer_group(),
			"territory": _default_territory(),
		}
	)
	customer_doc.flags.ignore_permissions = True
	customer_doc.insert(ignore_permissions=True)

	contact = frappe.get_doc(
		{
			"doctype": "Contact",
			"first_name": first_name or full_name,
			"last_name": last_name,
			"email_id": email or None,
		}
	)
	if email:
		contact.append("email_ids", {"email_id": email, "is_primary": 1})
	if phone:
		contact.append("phone_nos", {"phone": phone, "is_primary_mobile_no": 1})
	contact.append("links", {"link_doctype": "Customer", "link_name": customer_doc.name})
	contact.flags.ignore_permissions = True
	contact.insert(ignore_permissions=True)

	# Frappe's own Contact.validate() auto-links `user` to any User whose email
	# matches `email_id` — including someone else's registered account, if a
	# guest happens to type their email. Left alone, that silently makes this
	# guest Contact indistinguishable from the real account's Contact wherever
	# `{"user": ...}` is looked up (get_customer_for_user included), which could
	# attribute a real customer's future orders to this stranger's guest
	# Customer. Clearing it via db.set_value (not another .save(), which would
	# just re-trigger the same auto-link) severs that unintended link — a guest
	# checkout must never attach to anyone's account, registered or not.
	if contact.user:
		frappe.db.set_value("Contact", contact.name, "user", None, update_modified=False)

	return customer_doc.name, contact.name


@frappe.whitelist(allow_guest=True, methods=["POST"])
def register(full_name, email, password, mobile_no=None, subscribe=0):
	"""Self-service customer registration.

	Creates the User/Customer/Contact set, signs the visitor in using Frappe's
	own session handling, and hands their guest cart over.
	"""
	email = (email or "").strip().lower()
	full_name = (full_name or "").strip()
	mobile_no = (mobile_no or "").strip() or None

	if not full_name:
		frappe.throw("Please tell us your name.")

	validate_email_address(email, throw=True)

	if len(password or "") < MIN_PASSWORD_LENGTH:
		frappe.throw(f"Please choose a password of at least {MIN_PASSWORD_LENGTH} characters.")

	if frappe.db.exists("User", email):
		frappe.throw("An account with that email already exists. Try signing in instead.")

	parts = full_name.split(" ", 1)

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": escape_html(parts[0]),
			"last_name": escape_html(parts[1]) if len(parts) > 1 else None,
			"mobile_no": mobile_no,
			"enabled": 1,
			# Website User is the whole reason self-registered customers can
			# never reach /app — Frappe's www/app.py rejects this user_type.
			"user_type": "Website User",
			"send_welcome_email": 1,
		}
	)
	user.flags.ignore_permissions = True
	user.insert(ignore_permissions=True)

	# Frappe applies its own password policy on save.
	user.new_password = password
	user.save(ignore_permissions=True)

	if not user.get("roles"):
		user.add_roles(CUSTOMER_ROLE)

	_assert_no_desk_access(user)

	customer, contact = create_customer_and_contact(user, mobile_no)

	# Scope this user to their own Customer record so they can never resolve
	# another customer's data.
	from lapmarkaz_app.setup.portal_setup import ensure_user_permission

	ensure_user_permission(user.name, customer)

	if cint(subscribe):
		_subscribe_to_newsletter(email)

	frappe.db.commit()

	# Deliberately NOT signing the user in here. Registration proves an email
	# was typed, not that it belongs to the person typing it, so they have to
	# authenticate with the credentials they just chose. The guest cart is left
	# untouched: it merges on the login that follows (hooks.on_session_creation).
	needs_verification = _email_verification_required(user)

	return {
		"ok": True,
		"redirect": f"/login?registered=1{'&verify=1' if needs_verification else ''}",
		"message": (
			"Please verify your email, then log in."
			if needs_verification
			else "Registration successful — please log in."
		),
		"needs_verification": needs_verification,
		"user": user.name,
		"customer": customer,
		"contact": contact,
	}


def _email_verification_required(user):
	"""True when the account cannot be used until the address is confirmed."""
	# Frappe marks the account unusable until verified by disabling it.
	return not frappe.db.get_value("User", user.name, "enabled")


def _assert_no_desk_access(user):
	"""A self-registered shopper must never end up a System User.

	User.set_system_user() recomputes user_type from role desk_access on every
	save, so a role carrying desk_access silently grants Desk access. Config
	should prevent it (see setup/portal_setup.py), but this is a security
	boundary — enforce it here too rather than trusting configuration.
	"""
	current = frappe.db.get_value("User", user.name, "user_type")
	if current == "Website User":
		return

	frappe.db.set_value("User", user.name, "user_type", "Website User", update_modified=False)
	frappe.log_error(
		title="Lapmarkaz: registration produced a System User",
		message=(
			f"{user.name} was created as {current!r} instead of 'Website User'. "
			"Forced back to Website User. Check desk_access on the roles assigned "
			"at registration (see setup/portal_setup.py)."
		),
	)


def _subscribe_to_newsletter(email):
	from lapmarkaz_app.api.newsletter import email_group

	try:
		group = email_group()
		if not frappe.db.exists("Email Group Member", {"email": email, "email_group": group}):
			frappe.get_doc(
				{"doctype": "Email Group Member", "email_group": group, "email": email}
			).insert(ignore_permissions=True)
	except Exception:
		frappe.log_error("Lapmarkaz: newsletter subscribe failed")


def block_website_users_from_desk():
	"""hooks.before_request — send Website Users away from /app.

	Frappe already refuses them with a PermissionError; this turns that dead
	end into a redirect back to the customer portal.

	Note this raises werkzeug's RequestRedirect rather than frappe.Redirect:
	before_request runs in init_request, well before the website renderer that
	knows how to handle frappe.Redirect. RequestRedirect is an HTTPException,
	which frappe's application() already catches and returns verbatim.
	"""
	from werkzeug.routing import RequestRedirect

	request = getattr(frappe.local, "request", None)
	if not request:
		return

	path = request.path or ""
	if path != "/app" and not path.startswith("/app/"):
		return

	user = getattr(frappe.session, "user", None)
	if not user or user == "Guest":
		# Guests are Frappe's own business: it sends them to /login.
		return

	if frappe.db.get_value("User", user, "user_type") == "Website User":
		raise RequestRedirect("/account")
