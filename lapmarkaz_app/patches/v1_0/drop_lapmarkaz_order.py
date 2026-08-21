# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Retire the storefront-only order doctypes.

Website checkout writes an ERPNext Sales Order now (see
`lapmarkaz_app.api.order`), so Lapmarkaz Order and its child table have no
readers left. Any rows still in them predate the switch and are migrated
across first — dropping the table would otherwise take the order history with
it.
"""

import frappe

ORDER = "Lapmarkaz Order"
ORDER_ITEM = "Lapmarkaz Order Item"


def execute():
	if frappe.db.exists("DocType", ORDER):
		_carry_over_orders()

	for doctype in (ORDER, ORDER_ITEM):
		if frappe.db.exists("DocType", doctype):
			frappe.delete_doc("DocType", doctype, force=1, ignore_missing=True)

	_drop_tables()
	_drop_workspace_links()


def _drop_tables():
	"""Drop the physical tables the DocTypes leave behind.

	`delete_doc` only drops the table when it can still load the DocType's
	controller, and by the time this patch runs the doctype folders are gone
	from the app — so the row disappears from tabDocType while `tabLapmarkaz
	Order` lingers, holding the name against any future doctype.
	"""
	for doctype in (ORDER, ORDER_ITEM):
		if frappe.db.exists("DocType", doctype):
			continue
		frappe.db.sql_ddl(f"DROP TABLE IF EXISTS `tab{doctype}`")


def _carry_over_orders():
	"""Re-raise any legacy order as a draft Sales Order.

	Best effort by design: a legacy row whose customer or catalogue record has
	since been deleted can't become a valid Sales Order, and failing the whole
	migrate over it would be worse than leaving it behind. Anything skipped is
	logged with its original name so it can be recovered from the error log.
	"""
	from lapmarkaz_app.api.order import selling_company, selling_price_list
	from lapmarkaz_app.utils.items import get_or_create_item

	legacy = frappe.get_all(ORDER, pluck="name")
	if not legacy:
		return

	company = selling_company()
	currency = frappe.db.get_value("Company", company, "default_currency")
	price_list = selling_price_list()

	for name in legacy:
		try:
			_convert(frappe.get_doc(ORDER, name), company, currency, price_list)
		except Exception:
			frappe.log_error(
				title=f"Could not migrate {ORDER} {name} to Sales Order",
				message=frappe.get_traceback(),
			)


def _convert(old, company, currency, price_list):
	order = frappe.new_doc("Sales Order")
	order.update(
		{
			"customer": old.customer,
			"order_type": "Sales",
			"company": company,
			"transaction_date": old.order_date or old.creation,
			"delivery_date": old.expected_delivery or old.order_date or old.creation,
			"currency": currency,
			"conversion_rate": 1,
			"selling_price_list": price_list,
			"price_list_currency": currency,
			"plc_conversion_rate": 1,
			"ignore_pricing_rule": 1,
			"contact_email": old.email,
			"contact_phone": old.phone,
			"lm_web_order": 1,
			"lm_status": old.status,
			"lm_user": old.user,
			"lm_access_token": old.access_token,
			"lm_customer_name": old.customer_name,
			"lm_email": old.email,
			"lm_phone": old.phone,
			"lm_address": old.address,
			"lm_address_line": old.address_line,
			"lm_city": old.city,
			"lm_postal_code": old.postal_code,
			"lm_country": old.country,
			"lm_payment_method": old.payment_method,
			"lm_payment_method_code": old.payment_method_code,
			"lm_mode_of_payment": old.mode_of_payment,
			"lm_payment_proof": old.payment_proof,
			"lm_payment_status": old.payment_status,
			"lm_shipping_charge": old.shipping_charge,
		}
	)

	for row in old.items:
		order.append(
			"items",
			{
				"item_code": get_or_create_item(
					"Lapmarkaz Accessory" if row.item_type == "Accessory" else "Laptop",
					row.accessory if row.item_type == "Accessory" else row.laptop,
				),
				"item_name": row.item_name,
				"description": row.item_name,
				"qty": row.qty,
				"price_list_rate": row.rate,
				"rate": row.rate,
				"discount_percentage": 0,
				"delivery_date": order.delivery_date,
				"lm_item_type": row.item_type,
				"lm_laptop": row.laptop,
				"lm_accessory": row.accessory,
			},
		)

	if not order.items:
		return

	if old.discount_amount:
		order.apply_discount_on = "Net Total"
		order.discount_amount = old.discount_amount

	if old.shipping_charge:
		from lapmarkaz_app.api.order import shipping_account

		account = shipping_account(company)
		if account:
			order.append(
				"taxes",
				{
					"charge_type": "Actual",
					"account_head": account,
					"description": "Shipping",
					"tax_amount": old.shipping_charge,
				},
			)

	order.flags.ignore_permissions = True
	order.insert(ignore_permissions=True)


def _drop_workspace_links():
	"""Remove Desk links pointing at the retired doctype.

	The workspace fixture is already updated, but a site whose workspace was
	customised keeps its own rows — those would render as dead links.
	"""
	for table in ("Workspace Link", "Workspace Shortcut"):
		frappe.db.delete(table, {"link_to": ORDER})
