# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""About Us. Every string, image and link on this page comes from the
`About Page Settings` single — nothing here is hardcoded."""

import frappe

IMG = "/assets/lapmarkaz_app/images/"


def get_context(context):
	context.no_cache = 1

	settings = frappe.get_cached_doc("About Page Settings")
	context.about = settings

	context.hero_image = settings.hero_image or IMG + "about-office.svg"
	context.expertise_image_1 = settings.expertise_image_1 or IMG + "about-technician.svg"
	context.expertise_image_2 = settings.expertise_image_2 or IMG + "about-store.svg"

	context.title = settings.page_title or "About Us | HamzaTraders"
	context.description = settings.meta_description or ""

	# ---- shell -------------------------------------------------------------
	context.page_bg = "bg-white"
	context.header_layout = "search-left"
	context.show_wishlist = True
	context.search_placeholder = "Search laptops, accessories..."

	brands = frappe.get_all(
		"Laptop Brand", fields=["name"], order_by="display_order asc", limit_page_length=8
	)
	context.nav_items = [
		{"label": "Home", "href": "/"},
		{"label": "Shop", "href": "/shop"},
		{
			"label": "Brands",
			"href": "/shop",
			"dropdown": [{"label": b.name, "href": f"/shop?brand={b.name}"} for b in brands],
		},
		{"label": "About Us", "href": "/about", "active": True},
	]

	if settings.show_trust_strip:
		context.trust_strip = [
			{"icon": row.icon, "label": row.title} for row in settings.trust_items
		]

	context.footer_variant = "light-columns"
	context.footer_tagline = settings.footer_tagline
	context.footer_columns = _group_footer_links(settings.footer_links)
	context.footer_contact = {
		"title": "Connect",
		"email": settings.contact_email,
		"phone": settings.contact_phone,
	}
	context.footer_note = settings.footer_note

	return context


def _group_footer_links(rows):
	"""Flat child rows -> titled columns, preserving the order they're entered in."""
	columns = {}
	for row in rows:
		column = columns.setdefault(row.column_title, {"title": row.column_title, "links": []})
		column["links"].append({"label": row.label, "href": row.link or "/"})
	return list(columns.values())
