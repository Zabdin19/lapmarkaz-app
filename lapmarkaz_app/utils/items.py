# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Maps storefront catalogue records onto ERPNext Items.

Laptop and Lapmarkaz Accessory stay the source of truth for merchandising —
price, imagery, the stock badge shoppers see. ERPNext needs a real Item behind
every Sales Order line, so each catalogue record gets one provisioned the
first time it is ordered and linked back through its `item` field.

Provisioned Items are non-stock (`is_stock_item = 0`). Stock lives on the
Laptop record and is decremented by the storefront when Shop Settings asks
for it; letting ERPNext keep a second ledger would only produce two numbers
that disagree, and would force a warehouse onto every web order.
"""

import frappe
from frappe.utils import flt

# doctype -> (title field, price field, image field, item group)
CATALOGUE = {
	"Laptop": ("laptop_name", "price", "thumbnail", "Laptops"),
	"Lapmarkaz Accessory": ("accessory_name", "price", "image", "Accessories"),
	"Printing Machine": ("machine_name", "price", "thumbnail", "Printing Machines"),
	"Printing Accessory": ("accessory_name", "price", "image", "Printing Accessories"),
}

FALLBACK_ITEM_GROUP = "All Item Groups"


def _default_uom():
	for uom in ("Nos", "Unit"):
		if frappe.db.exists("UOM", uom):
			return uom
	return frappe.db.get_value("UOM", {}, "name")


def _item_group(group):
	if frappe.db.exists("Item Group", group):
		return group

	parent = FALLBACK_ITEM_GROUP
	if not frappe.db.exists("Item Group", parent):
		parent = frappe.db.get_value("Item Group", {"is_group": 1}, "name")

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
	return group


def _free_item_code(base):
	"""A free Item code near `base`.

	Laptops and accessories are both autonamed by their product name, so a
	laptop and an accessory can legitimately collide. Suffixing keeps the
	readable code for whichever got there first instead of failing checkout.
	"""
	base = (base or "").strip() or "Lapmarkaz Product"
	code = base
	suffix = 1
	while frappe.db.exists("Item", code):
		suffix += 1
		code = f"{base}-{suffix}"
	return code


def get_or_create_item(doctype, name):
	"""The Item code behind a catalogue record, provisioning one if needed."""
	if doctype not in CATALOGUE:
		frappe.throw(f"{doctype} is not a sellable catalogue doctype.", frappe.ValidationError)

	title_field, price_field, image_field, group = CATALOGUE[doctype]
	product = frappe.get_doc(doctype, name)

	linked = product.get("item")
	if linked and frappe.db.exists("Item", linked):
		return linked

	title = product.get(title_field) or name
	rate = flt(product.get(price_field))
	item = frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": _free_item_code(title),
			"item_name": title,
			"description": title,
			"item_group": _item_group(group),
			"stock_uom": _default_uom(),
			"is_stock_item": 0,
			"is_sales_item": 1,
			"is_purchase_item": 0,
			"include_item_in_manufacturing": 0,
			"image": product.get(image_field),
			# `standard_rate` is deliberately withheld until after the insert:
			# ERPNext's Item.after_insert reacts to it by creating an Item Price
			# *without* ignoring permissions, which fails outright for the guest
			# or website user whose order triggered this. We write the price
			# ourselves below instead.
		}
	)
	item.flags.ignore_permissions = True
	item.insert(ignore_permissions=True)

	item.db_set("standard_rate", rate, update_modified=False)
	_upsert_item_price(item.name, item.stock_uom, rate)

	# db_set rather than save: the caller is mid-checkout and has no business
	# re-running the product's validations, nor bumping its modified stamp.
	product.db_set("item", item.name, update_modified=False)

	return item.name


def _upsert_item_price(item_code, uom, rate):
	"""Mirror a product's price into the selling price list."""
	# Local import: api.order imports this module, so binding it at module
	# level would close the loop.
	from lapmarkaz_app.api.order import selling_price_list

	price_list = selling_price_list()
	if not price_list or not rate:
		return

	existing = frappe.db.get_value(
		"Item Price", {"item_code": item_code, "price_list": price_list, "uom": uom}, "name"
	)
	if existing:
		if flt(frappe.db.get_value("Item Price", existing, "price_list_rate")) != rate:
			frappe.db.set_value("Item Price", existing, "price_list_rate", rate)
		return

	doc = frappe.get_doc(
		{
			"doctype": "Item Price",
			"price_list": price_list,
			"item_code": item_code,
			"uom": uom,
			"currency": frappe.db.get_value("Price List", price_list, "currency"),
			"price_list_rate": rate,
		}
	)
	doc.flags.ignore_permissions = True
	doc.insert(ignore_permissions=True)


def sync_item(doc, method=None):
	"""Keep a provisioned Item's name, image and rate in step with its product.

	Hooked on Laptop / Lapmarkaz Accessory `on_update`. Products that have
	never been ordered have no Item yet and are left alone — one gets made
	when it is first sold.
	"""
	title_field, price_field, image_field, _group = CATALOGUE[doc.doctype]

	if not doc.get("item") or not frappe.db.exists("Item", doc.item):
		return

	title = doc.get(title_field) or doc.name
	rate = flt(doc.get(price_field))
	updates = {
		"item_name": title,
		"image": doc.get(image_field),
		"standard_rate": rate,
	}

	current = frappe.db.get_value("Item", doc.item, list(updates), as_dict=True)
	if not current or any(current.get(k) != v for k, v in updates.items()):
		frappe.db.set_value("Item", doc.item, updates)

	_upsert_item_price(doc.item, frappe.db.get_value("Item", doc.item, "stock_uom"), rate)
