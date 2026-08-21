# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Prepare ERPNext to receive storefront orders.

	bench --site site.localhost execute lapmarkaz_app.setup.erpnext_setup.run

Website checkout writes a real Sales Order, so ERPNext needs three things
this app can't assume are already there: a selling Company in the shop's
currency, the item groups the catalogue is provisioned into, and the custom
fields that carry storefront-only data (payment method, guest access token,
the address the shopper typed) alongside the standard Sales Order fields.

Everything here is idempotent — it runs on install and again after every
migrate, so a field added in a later release lands without a manual step.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

COMPANY = "Lapmarkaz"
ABBR = "LM"
COUNTRY = "Pakistan"
CURRENCY = "PKR"

ITEM_GROUPS = ("Laptops", "Accessories")

# Account used for the shipping line on a Sales Order, tried in order.
SHIPPING_ACCOUNT_CANDIDATES = ("Freight and Forwarding Charges", "Shipping Charges")

STOREFRONT_STATUSES = "Pending\nConfirmed\nPacked\nShipped\nDelivered\nCancelled"

CUSTOM_FIELDS = {
	"Sales Order": [
		{
			"fieldname": "lm_storefront_section",
			"label": "Lapmarkaz Storefront",
			"fieldtype": "Section Break",
			"insert_after": "terms",
			"collapsible": 1,
		},
		{
			"fieldname": "lm_web_order",
			"label": "Placed on Website",
			"fieldtype": "Check",
			"insert_after": "lm_storefront_section",
			"read_only": 1,
			"description": "Set by the storefront checkout. Distinguishes web orders from ones raised in the Desk.",
		},
		{
			"fieldname": "lm_status",
			"label": "Storefront Status",
			"fieldtype": "Select",
			"insert_after": "lm_web_order",
			"options": STOREFRONT_STATUSES,
			"default": "Pending",
			"in_standard_filter": 1,
			"description": "Drives the fulfilment timeline the customer sees on their order page.",
		},
		{
			"fieldname": "lm_user",
			"label": "Website User",
			"fieldtype": "Link",
			"options": "User",
			"insert_after": "lm_status",
			"read_only": 1,
		},
		{
			"fieldname": "lm_access_token",
			"label": "Access Token",
			"fieldtype": "Data",
			"insert_after": "lm_user",
			"hidden": 1,
			"no_copy": 1,
			"print_hide": 1,
			"read_only": 1,
			"description": "Set only for guest checkouts. Proves ownership of the confirmation page in place of a session, since a guest has none.",
		},
		{
			"fieldname": "lm_column_payment",
			"fieldtype": "Column Break",
			"insert_after": "lm_access_token",
		},
		{
			"fieldname": "lm_payment_method",
			"label": "Payment Method",
			"fieldtype": "Link",
			"options": "Lapmarkaz Payment Method",
			"insert_after": "lm_column_payment",
		},
		{
			"fieldname": "lm_payment_method_code",
			"label": "Payment Method Code",
			"fieldtype": "Data",
			"insert_after": "lm_payment_method",
			"read_only": 1,
			"description": "Machine key captured at order time; survives renames of the method.",
		},
		{
			"fieldname": "lm_mode_of_payment",
			"label": "Mode of Payment",
			"fieldtype": "Link",
			"options": "Mode of Payment",
			"insert_after": "lm_payment_method_code",
			"read_only": 1,
		},
		{
			"fieldname": "lm_payment_status",
			"label": "Payment Status",
			"fieldtype": "Select",
			"options": "Unpaid\nPaid\nRefunded",
			"default": "Unpaid",
			"insert_after": "lm_mode_of_payment",
		},
		{
			"fieldname": "lm_payment_proof",
			"label": "Payment Proof",
			"fieldtype": "Attach",
			"insert_after": "lm_payment_status",
			"description": "Receipt or screenshot, when the chosen method requires one.",
		},
		{
			"fieldname": "lm_delivery_section",
			"label": "Storefront Delivery Details",
			"fieldtype": "Section Break",
			"insert_after": "lm_payment_proof",
			"collapsible": 1,
		},
		{
			"fieldname": "lm_address",
			"label": "Storefront Address",
			"fieldtype": "Link",
			"options": "Lapmarkaz Address",
			"insert_after": "lm_delivery_section",
			"read_only": 1,
		},
		{
			"fieldname": "lm_address_line",
			"label": "Street Address",
			"fieldtype": "Small Text",
			"insert_after": "lm_address",
		},
		{
			"fieldname": "lm_city",
			"label": "City",
			"fieldtype": "Data",
			"insert_after": "lm_address_line",
		},
		{
			"fieldname": "lm_postal_code",
			"label": "Postal Code",
			"fieldtype": "Data",
			"insert_after": "lm_city",
		},
		{
			"fieldname": "lm_column_delivery",
			"fieldtype": "Column Break",
			"insert_after": "lm_postal_code",
		},
		{
			"fieldname": "lm_country",
			"label": "Country",
			"fieldtype": "Data",
			"insert_after": "lm_column_delivery",
			"default": COUNTRY,
		},
		{
			"fieldname": "lm_customer_name",
			"label": "Shipping Name",
			"fieldtype": "Data",
			"insert_after": "lm_country",
			"description": "The name the shopper typed at checkout, which may differ from the Customer record.",
		},
		{
			"fieldname": "lm_phone",
			"label": "Phone",
			"fieldtype": "Data",
			"insert_after": "lm_customer_name",
		},
		{
			"fieldname": "lm_email",
			"label": "Email",
			"fieldtype": "Data",
			"options": "Email",
			"insert_after": "lm_phone",
		},
		{
			"fieldname": "lm_shipping_charge",
			"label": "Shipping Charge",
			"fieldtype": "Currency",
			"insert_after": "lm_email",
			"read_only": 1,
			"description": "Mirrors the shipping row in Sales Taxes and Charges, so the storefront can show it without parsing the tax table.",
		},
	],
	"Sales Order Item": [
		{
			"fieldname": "lm_item_type",
			"label": "Storefront Item Type",
			"fieldtype": "Select",
			"options": "\nLaptop\nAccessory",
			"insert_after": "brand",
			"read_only": 1,
		},
		{
			"fieldname": "lm_laptop",
			"label": "Laptop",
			"fieldtype": "Link",
			"options": "Laptop",
			"insert_after": "lm_item_type",
			"read_only": 1,
		},
		{
			"fieldname": "lm_accessory",
			"label": "Accessory",
			"fieldtype": "Link",
			"options": "Lapmarkaz Accessory",
			"insert_after": "lm_laptop",
			"read_only": 1,
		},
	],
}


def install_custom_fields():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	return sum(len(v) for v in CUSTOM_FIELDS.values())


def ensure_currency_defaults():
	"""Point the site's money at the shop's currency rather than ERPNext's default."""
	if not frappe.db.exists("Currency", CURRENCY):
		return "currency missing"

	frappe.db.set_single_value("Global Defaults", "default_currency", CURRENCY)
	frappe.db.set_default("currency", CURRENCY)
	return CURRENCY


def default_company():
	"""The company the site sells from, ignoring ERPNext's demo dataset.

	A site that ran the setup wizard ends up with two companies: the real one
	and a "<name> (Demo)" holding sample transactions. They look alike to a
	plain Company query, and filing live web orders into the throwaway books is
	not a mistake that announces itself — so the demo company is excluded by
	name, and the site's own default is preferred over guessing.
	"""
	demo = frappe.db.get_single_value("Global Defaults", "demo_company")

	for candidate in (
		frappe.db.get_single_value("Global Defaults", "default_company"),
		frappe.defaults.get_user_default("Company"),
	):
		if candidate and candidate != demo and frappe.db.exists("Company", candidate):
			return candidate

	return frappe.db.get_value("Company", {"name": ("!=", demo)} if demo else {}, "name")


def ensure_company():
	"""The selling company. Reuses whatever is already configured."""
	existing = default_company()
	if existing:
		return existing

	company = frappe.get_doc(
		{
			"doctype": "Company",
			"company_name": COMPANY,
			"abbr": ABBR,
			"default_currency": CURRENCY,
			"country": COUNTRY,
		}
	)
	company.flags.ignore_permissions = True
	company.insert(ignore_permissions=True)
	return company.name


def ensure_price_list(company):
	"""A selling price list in the company currency.

	ERPNext refuses a Sales Order whose price list currency disagrees with the
	order currency, and the stock "Standard Selling" list is created in
	whatever currency the site defaulted to at install time.
	"""
	currency = frappe.db.get_value("Company", company, "default_currency") or CURRENCY
	name = "Standard Selling"

	if not frappe.db.exists("Price List", name):
		doc = frappe.get_doc(
			{
				"doctype": "Price List",
				"price_list_name": name,
				"selling": 1,
				"enabled": 1,
				"currency": currency,
			}
		)
		doc.flags.ignore_permissions = True
		doc.insert(ignore_permissions=True)
		return name

	if frappe.db.get_value("Price List", name, "currency") != currency:
		frappe.db.set_value("Price List", name, "currency", currency)

	return name


def ensure_item_groups():
	parent = "All Item Groups"
	if not frappe.db.exists("Item Group", parent):
		parent = frappe.db.get_value("Item Group", {"is_group": 1}, "name")

	created = []
	for group in ITEM_GROUPS:
		if frappe.db.exists("Item Group", group):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": group,
				"parent_item_group": parent,
				"is_group": 0,
			}
		)
		doc.flags.ignore_permissions = True
		doc.insert(ignore_permissions=True)
		created.append(group)

	return created


def ensure_shipping_account(company):
	"""The account the shipping charge is booked against.

	Shipping is carried as an "Actual" row in Sales Taxes and Charges so it
	lands in `grand_total` like any other charge — which means it needs a real
	account. The standard chart of accounts usually has one; if not, we add a
	leaf under the company's expense root rather than leaving checkout broken.
	"""
	abbr = frappe.db.get_value("Company", company, "abbr")

	for candidate in SHIPPING_ACCOUNT_CANDIDATES:
		name = f"{candidate} - {abbr}"
		if frappe.db.exists("Account", name):
			return name

	parent = frappe.db.get_value(
		"Account",
		{"company": company, "account_name": "Indirect Expenses", "is_group": 1},
		"name",
	) or frappe.db.get_value(
		"Account", {"company": company, "root_type": "Expense", "is_group": 1}, "name"
	)

	if not parent:
		return None

	doc = frappe.get_doc(
		{
			"doctype": "Account",
			"account_name": SHIPPING_ACCOUNT_CANDIDATES[-1],
			"parent_account": parent,
			"company": company,
			"account_type": "Chargeable",
			"root_type": "Expense",
			"is_group": 0,
		}
	)
	doc.flags.ignore_permissions = True
	doc.insert(ignore_permissions=True)
	return doc.name


def ensure_shop_settings(company, shipping_account):
	"""Record the resolved company and shipping account on Shop Settings.

	Staff can point either somewhere else afterwards; checkout reads these
	first and only falls back to discovery when they're blank.
	"""
	settings = frappe.get_single("Lapmarkaz Shop Settings")

	changed = []
	if not settings.company and company:
		settings.company = company
		changed.append("company")
	if not settings.shipping_account and shipping_account:
		settings.shipping_account = shipping_account
		changed.append("shipping_account")

	if changed:
		settings.flags.ignore_permissions = True
		settings.save(ignore_permissions=True)

	return changed


def run():
	fields = install_custom_fields()
	currency = ensure_currency_defaults()
	company = ensure_company()
	price_list = ensure_price_list(company)
	groups = ensure_item_groups()
	shipping_account = ensure_shipping_account(company)
	changed = ensure_shop_settings(company, shipping_account)
	frappe.db.commit()

	print(f"Custom fields    : {fields}")
	print(f"Currency         : {currency}")
	print(f"Company          : {company}")
	print(f"Price list       : {price_list}")
	print(f"Item groups      : {groups or 'already present'}")
	print(f"Shipping account : {shipping_account or 'NOT RESOLVED — set it on Shop Settings'}")
	print(f"Shop Settings    : {changed or 'unchanged'}")


def after_migrate():
	"""Keep custom fields in step with the app without a manual run."""
	install_custom_fields()
