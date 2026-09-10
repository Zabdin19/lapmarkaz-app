# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Product detail page, served at /laptops/<slug> via hooks.website_route_rules."""

import frappe

from lapmarkaz_app.api.wishlist import wishlisted_names
from lapmarkaz_app.www.shop import CARD_FIELDS


def get_context(context):
	context.no_cache = 1

	slug = frappe.form_dict.get("slug")
	name = frappe.db.get_value("Laptop", {"slug": slug, "published": 1}, "name")
	if not name:
		frappe.throw("Laptop not found", frappe.DoesNotExistError)

	laptop = frappe.get_doc("Laptop", name)
	context.laptop = laptop
	context.title = f"{laptop.brand} {laptop.model} | hamzatraders"

	context.gallery = [row.image for row in laptop.images if row.image] or [laptop.thumbnail]

	context.spec_groups = [
		{
			"label": "Processor (CPU)",
			"value": laptop.processor,
			"note": laptop.processor_note,
		},
		{
			"label": "Memory (RAM)",
			"value": laptop.ram_spec or f"{laptop.ram_gb}GB",
			"note": laptop.ram_note,
		},
		{"label": "Storage", "value": laptop.storage, "note": laptop.storage_note},
		{"label": "Display", "value": laptop.display, "note": laptop.display_note},
		{"label": "Battery", "value": laptop.battery, "note": laptop.battery_note},
		{"label": "Ports & Connectivity", "value": laptop.ports, "note": laptop.ports_note},
		# The three rows above mirror the reference design; GPU and condition
		# follow so the full spec sheet is on the page.
		{"label": "Graphics (GPU)", "value": laptop.gpu, "note": laptop.gpu_note},
		{
			"label": "Condition",
			"value": laptop.condition,
			"note": f"Grade {laptop.grade} · {laptop.warranty}" if laptop.grade else laptop.warranty,
		},
	]
	context.spec_groups = [s for s in context.spec_groups if s["value"]]

	context.assurances = [
		{"icon": "truck", "label": laptop.shipping_note or "Free Nationwide Shipping"},
		{"icon": "box", "label": laptop.return_note or "7-Day Easy Return"},
		{"icon": "shield", "label": laptop.warranty or "Warranty Included"},
	]

	context.reviews = frappe.get_all(
		"Laptop Review",
		filters={"laptop": name},
		fields=["reviewer_name", "rating", "title", "comment", "review_date", "verified_purchase"],
		order_by="creation desc",
		limit_page_length=8,
	)

	context.related = _related(laptop)
	context.wishlist_ids = wishlisted_names()

	context.breadcrumbs = [
		{"label": "Home", "href": "/"},
		{"label": "Laptops", "href": "/shop"},
		{"label": laptop.brand, "href": f"/shop?brand={laptop.brand}"},
		{"label": laptop.model, "href": None},
	]

	# ---- shell -------------------------------------------------------------
	context.page_bg = "bg-white"
	context.header_layout = "search-center"
	context.search_placeholder = "Search laptops, accessories..."
	context.show_wishlist = True
	context.nav_items = [
		{"label": "Laptops", "href": "/shop", "active": True},
		{"label": "Accessories", "href": "/accessories"},
		{"label": "Printing Machines", "href": "/printing-machines"},
		{"label": "Printing Accessories", "href": "/printing-accessories"},
		{"label": "Support", "href": "/support"},
	]

	context.footer_variant = "full"
	context.footer_blurb = (
		"Your trusted destination for premium refurbished laptops in Pakistan. "
		"High quality, great value, guaranteed."
	)
	context.footer_columns = [
		{
			"title": "Company",
			"links": [
				{"label": "About Us", "href": "/about"},
				{"label": "Contact Us", "href": "/contact"},
			],
		},
		{
			"title": "Customer Care",
			"links": [
				{"label": "Warranty Policy", "href": "/warranty"},
				{"label": "Shipping & Returns", "href": "/shipping"},
			],
		},
		{
			"title": "Legal",
			"links": [
				{"label": "Privacy Policy", "href": "/privacy"},
				{"label": "Terms of Service", "href": "/terms"},
			],
		},
	]
	context.footer_note = "© 2024 hamzatraders Pakistan. All rights reserved."

	return context


def _related(laptop, limit=4):
	"""Comparable machines in a similar price band, across brands."""
	seen = {laptop.name}
	picks = []

	def collect(filters):
		for row in frappe.get_all(
			"Laptop",
			filters=filters,
			fields=CARD_FIELDS,
			order_by="rating desc, review_count desc, creation desc",
			limit_page_length=limit * 3,
		):
			if row.name not in seen and len(picks) < limit:
				seen.add(row.name)
				picks.append(row)

	low, high = laptop.price * 0.55, laptop.price * 1.75
	collect({"published": 1, "price": ["between", [low, high]], "name": ["not in", list(seen)]})

	if len(picks) < limit:
		collect({"published": 1, "name": ["not in", list(seen)]})

	return picks[:limit]
