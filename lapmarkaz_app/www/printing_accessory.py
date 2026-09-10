# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Product detail page, served at /printing-accessories/<slug> via
hooks.website_route_rules."""

import frappe

from lapmarkaz_app.www.printing_accessories import CARD_FIELDS


def get_context(context):
	context.no_cache = 1

	slug = frappe.form_dict.get("slug")
	name = frappe.db.get_value("Printing Accessory", {"slug": slug, "published": 1}, "name")
	if not name:
		frappe.throw("Printing accessory not found", frappe.DoesNotExistError)

	accessory = frappe.get_doc("Printing Accessory", name)
	context.accessory = accessory
	context.title = f"{accessory.accessory_name} | hamzatraders"

	context.spec_groups = [s for s in [
		{"label": "Brand", "value": accessory.brand, "note": None},
		{"label": "Type", "value": accessory.accessory_type, "note": None},
	] if s["value"]]

	context.compatible_machines = _compatible_machines(accessory)
	context.related = _related(accessory)

	context.breadcrumbs = [
		{"label": "Home", "href": "/"},
		{"label": "Printing Accessories", "href": "/printing-accessories"},
		{"label": accessory.brand, "href": f"/printing-accessories?brand={accessory.brand}"} if accessory.brand else None,
		{"label": accessory.accessory_name, "href": None},
	]
	context.breadcrumbs = [c for c in context.breadcrumbs if c]

	# ---- shell -------------------------------------------------------------
	context.page_bg = "bg-white"
	context.header_layout = "search-center"
	context.search_placeholder = "Search printing accessories..."
	context.show_wishlist = False
	context.nav_items = [
		{"label": "Laptops", "href": "/shop"},
		{"label": "Accessories", "href": "/accessories"},
		{"label": "Printing Machines", "href": "/printing-machines"},
		{"label": "Printing Accessories", "href": "/printing-accessories", "active": True},
		{"label": "Support", "href": "/support"},
	]
	context.footer_variant = "slim"
	context.footer_note = "© 2024 hamzatraders. Premium Tech for Pakistan."
	context.footer_links = [
		{"label": "Warranty Policy", "href": "/warranty"},
		{"label": "Shipping Info", "href": "/shipping"},
		{"label": "Privacy", "href": "/privacy"},
		{"label": "Terms of Service", "href": "/terms"},
	]

	return context


def _compatible_machines(accessory, limit=8):
	names = [row.machine for row in accessory.compatible_machines if row.machine]
	if not names:
		return []
	return frappe.get_all(
		"Printing Machine",
		filters={"name": ["in", names], "published": 1},
		fields=["name", "brand", "model", "slug", "tagline", "price", "thumbnail", "stock_status"],
		limit_page_length=limit,
	)


def _related(accessory, limit=4):
	"""Other accessories of the same type, excluding this one."""
	if not accessory.accessory_type:
		return []
	return frappe.get_all(
		"Printing Accessory",
		filters={
			"published": 1,
			"accessory_type": accessory.accessory_type,
			"name": ["!=", accessory.name],
		},
		fields=CARD_FIELDS,
		order_by="is_featured desc, creation desc",
		limit_page_length=limit,
	)
