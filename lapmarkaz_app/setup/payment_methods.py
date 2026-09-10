# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Seed the checkout payment methods.

	bench --site site.localhost execute lapmarkaz_app.setup.payment_methods.run

Re-runnable. Each record is matched on `method_code`, so renaming a method's
display label in Desk will not cause a duplicate to be seeded.
"""

import frappe

# code, name, description, mode_of_payment, flags
#
# Only Cash on Delivery is live. The rest are seeded disabled so they are ready
# to switch on in Desk once the account and wallet numbers below are real ones
# — the values here are placeholders, and an enabled method sends shoppers to
# them. `is_enabled` is part of each spec, so re-running this seed keeps that
# choice rather than turning everything back on.
METHODS = [
	{
		"method_code": "cod",
		"method_name": "Cash on Delivery",
		"description": "Pay the rider when your order arrives.",
		"mode_of_payment": "Cash",
		"is_default": 1,
		"display_order": 1,
	},
	{
		"is_enabled": 0,
		"method_code": "card",
		"method_name": "Credit / Debit Card",
		"description": "Visa and Mastercard accepted.",
		"mode_of_payment": "Credit Card",
		"display_order": 2,
	},
	{
		"is_enabled": 0,
		"method_code": "bank_transfer",
		"method_name": "Bank Transfer",
		"description": "Transfer to our account and share the receipt.",
		"mode_of_payment": "Wire Transfer",
		"requires_proof": 1,
		"display_order": 3,
		"instructions": (
			"<p>Transfer the total to:</p>"
			"<p><b>hamzatraders</b><br>Meezan Bank<br>"
			"Account: 0123 4567 8901 2345<br>"
			"IBAN: PK00 MEZN 0001 2345 6789 0123</p>"
			"<p>Upload the transfer receipt below so we can verify it.</p>"
		),
	},
	{
		"is_enabled": 0,
		"method_code": "easypaisa",
		"method_name": "Easypaisa",
		"description": "Pay from your Easypaisa wallet.",
		"mode_of_payment": "Easypaisa",
		"requires_proof": 1,
		"display_order": 4,
		"instructions": (
			"<p>Send the total to Easypaisa wallet <b>0321 2789920</b> "
			"(hamzatraders), then upload the confirmation screenshot below.</p>"
		),
	},
	{
		"is_enabled": 0,
		"method_code": "jazzcash",
		"method_name": "JazzCash",
		"description": "Pay from your JazzCash wallet.",
		"mode_of_payment": "JazzCash",
		"requires_proof": 1,
		"display_order": 5,
		"instructions": (
			"<p>Send the total to JazzCash wallet <b>0321 2789920</b> "
			"(hamzatraders), then upload the confirmation screenshot below.</p>"
		),
	},
]

# Wallet providers ERPNext does not ship as standard Modes of Payment.
EXTRA_MODES = [("Easypaisa", "Bank"), ("JazzCash", "Bank")]


def _ensure_modes_of_payment():
	created = []
	for name, mode_type in EXTRA_MODES:
		if not frappe.db.exists("Mode of Payment", name):
			frappe.get_doc(
				{"doctype": "Mode of Payment", "mode_of_payment": name, "type": mode_type, "enabled": 1}
			).insert(ignore_permissions=True)
			created.append(name)
	return created


def run():
	created_modes = _ensure_modes_of_payment()

	for spec in METHODS:
		values = dict(spec)
		values.setdefault("is_enabled", 1)

		# Drop any accounting link that does not exist on this site rather than
		# failing the whole seed.
		if values.get("mode_of_payment") and not frappe.db.exists(
			"Mode of Payment", values["mode_of_payment"]
		):
			values["mode_of_payment"] = None

		existing = frappe.db.get_value(
			"Lapmarkaz Payment Method", {"method_code": values["method_code"]}, "name"
		)
		if existing:
			doc = frappe.get_doc("Lapmarkaz Payment Method", existing)
			doc.update(values)
			doc.save(ignore_permissions=True)
		else:
			frappe.get_doc({"doctype": "Lapmarkaz Payment Method", **values}).insert(
				ignore_permissions=True
			)

	frappe.db.commit()

	print("Modes of Payment created:", created_modes or "none needed")
	for row in frappe.get_all(
		"Lapmarkaz Payment Method",
		fields=["method_code", "method_name", "is_enabled", "is_default", "requires_proof", "mode_of_payment"],
		order_by="display_order asc",
	):
		print(
			f"  {row.method_code:14s} {row.method_name:22s} "
			f"enabled={row.is_enabled} default={row.is_default} "
			f"proof={row.requires_proof} mop={row.mode_of_payment}"
		)
