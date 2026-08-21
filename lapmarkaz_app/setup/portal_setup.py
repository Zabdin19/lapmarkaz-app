# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Configure the customer portal.

	bench --site site.localhost execute lapmarkaz_app.setup.portal_setup.run

Idempotent. Covers the site-level settings that self-registration depends on,
plus the record-level permissions that keep one customer out of another
customer's data.
"""

import frappe

CUSTOMER_ROLE = "Customer"

# doctype -> permission rules for the Customer role. `if_owner` restricts a
# customer to rows they created; Customer/Address additionally rely on the
# User Permission created at registration.
# Sales Order is deliberately absent: order history is read server-side by
# lapmarkaz_app.utils.orders, filtered to the session user, so shoppers never
# need read on the document itself.
CUSTOMER_PERMS = [
	{"doctype": "Lapmarkaz Address", "read": 1, "write": 1, "create": 1, "if_owner": 1},
	{"doctype": "Lapmarkaz Wishlist Item", "read": 1, "write": 1, "create": 1, "if_owner": 1},
]


def _make_customer_role_portal_only():
	"""Strip Desk access from the Customer role.

	User.set_system_user() recomputes user_type on every save as
	"System User" if any assigned role has desk_access, else "Website User".
	With desk_access=1 on Customer, assigning that role to a self-registered
	shopper silently promotes them to a System User with full Desk access.
	Customer is a portal role, so desk_access belongs at 0.
	"""
	if not frappe.db.exists("Role", CUSTOMER_ROLE):
		return "role missing"

	if frappe.db.get_value("Role", CUSTOMER_ROLE, "desk_access"):
		role = frappe.get_doc("Role", CUSTOMER_ROLE)
		role.desk_access = 0
		role.save(ignore_permissions=True)
		return "desk_access disabled"
	return "already portal-only"


def _demote_stray_website_users():
	"""Repair any self-registered customer already promoted to System User."""
	repaired = []
	for user in frappe.get_all(
		"User",
		filters={"user_type": "System User", "enabled": 1},
		fields=["name"],
	):
		if user.name in ("Administrator", "Guest"):
			continue

		roles = {r.role for r in frappe.get_all("Has Role", filters={"parent": user.name}, fields=["role"])}
		# Only touch accounts whose sole role is Customer — never staff.
		if roles and roles.issubset({CUSTOMER_ROLE, "All"}):
			doc = frappe.get_doc("User", user.name)
			doc.user_type = "Website User"
			doc.save(ignore_permissions=True)
			repaired.append(user.name)

	return repaired


def _enable_signup():
	website = frappe.get_single("Website Settings")
	if website.disable_signup:
		website.disable_signup = 0
		website.save(ignore_permissions=True)
		return "enabled"
	return "already enabled"


def _set_portal_default_role():
	portal = frappe.get_single("Portal Settings")
	if portal.default_role != CUSTOMER_ROLE:
		portal.default_role = CUSTOMER_ROLE
		portal.save(ignore_permissions=True)
		return f"set to {CUSTOMER_ROLE}"
	return "already set"


def _apply_customer_perms():
	"""Grant the Customer role owner-scoped access to storefront doctypes."""
	from frappe.permissions import add_permission, update_permission_property

	applied = []
	for rule in CUSTOMER_PERMS:
		doctype = rule["doctype"]
		if not frappe.db.exists("DocType", doctype):
			continue

		existing = frappe.db.exists(
			"Custom DocPerm", {"parent": doctype, "role": CUSTOMER_ROLE, "permlevel": 0}
		)
		if not existing:
			add_permission(doctype, CUSTOMER_ROLE, 0)

		for prop in ("read", "write", "create", "if_owner"):
			update_permission_property(doctype, CUSTOMER_ROLE, 0, prop, rule[prop])

		# Customers must never delete storefront records.
		update_permission_property(doctype, CUSTOMER_ROLE, 0, "delete", 0)
		applied.append(doctype)

	return applied


def ensure_user_permission(user, customer):
	"""Pin a website user to their own Customer record.

	With this in place a customer can only ever resolve their own Customer,
	and anything linked to it, regardless of what they ask for.
	"""
	if not customer:
		return False

	exists = frappe.db.exists(
		"User Permission",
		{"user": user, "allow": "Customer", "for_value": customer},
	)
	if exists:
		return False

	frappe.get_doc(
		{
			"doctype": "User Permission",
			"user": user,
			"allow": "Customer",
			"for_value": customer,
			"apply_to_all_doctypes": 1,
		}
	).insert(ignore_permissions=True)
	return True


def run():
	print("Customer role desk access:", _make_customer_role_portal_only())
	print("Website Settings signup  :", _enable_signup())
	print("Portal Settings role     :", _set_portal_default_role())
	print("Customer role perms on   :", _apply_customer_perms())
	print("Demoted stray System Users:", _demote_stray_website_users() or "none")

	frappe.db.commit()
	print("\nPortal setup complete.")
