# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Contact form on /support. Each submission becomes a Lapmarkaz Support Message."""

import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import now, strip_html, validate_email_address

MAX_MESSAGE = 4000


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="email", limit=5, seconds=60 * 10)
def send_message(sender_name, email, message):
	sender_name = strip_html((sender_name or "").strip())
	email = (email or "").strip().lower()
	message = strip_html((message or "").strip())

	if not sender_name:
		frappe.throw("Please tell us your name.")
	if not message:
		frappe.throw("Please write a message.")
	if len(message) > MAX_MESSAGE:
		frappe.throw(f"Please keep your message under {MAX_MESSAGE} characters.")

	validate_email_address(email, throw=True)

	doc = frappe.get_doc(
		{
			"doctype": "Lapmarkaz Support Message",
			"sender_name": sender_name,
			"email": email,
			"message": message,
			"status": "New",
			"received_on": now(),
			"source_page": "/support",
			"user": None if frappe.session.user == "Guest" else frappe.session.user,
		}
	)
	doc.insert(ignore_permissions=True)

	_notify(doc)

	settings = frappe.get_cached_doc("Support Page Settings")
	return {
		"ok": True,
		"message": settings.contact_success_message
		or "Thanks — we've got your message and will reply shortly.",
	}


def _notify(doc):
	"""Best-effort alert; a mail failure must not lose the message."""
	recipient = frappe.db.get_single_value("Support Page Settings", "notify_email")
	if not recipient:
		return

	try:
		frappe.sendmail(
			recipients=[recipient],
			subject=f"New support message from {doc.sender_name}",
			message=(
				f"<p><b>From:</b> {frappe.utils.escape_html(doc.sender_name)} "
				f"&lt;{frappe.utils.escape_html(doc.email)}&gt;</p>"
				f"<p>{frappe.utils.escape_html(doc.message).replace(chr(10), '<br>')}</p>"
			),
			reference_doctype=doc.doctype,
			reference_name=doc.name,
		)
	except Exception:
		frappe.log_error("Lapmarkaz: support notification failed")
