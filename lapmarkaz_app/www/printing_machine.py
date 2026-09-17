# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Product detail page, served at /printing-machines/<slug> via
hooks.website_route_rules. Mirrors www/laptop.py."""

import frappe

from lapmarkaz_app.www.printing_machines import CARD_FIELDS


def get_context(context):
	context.no_cache = 1

	slug = frappe.form_dict.get("slug")
	name = frappe.db.get_value("Printing Machine", {"slug": slug, "published": 1}, "name")
	if not name:
		frappe.throw("Printing machine not found", frappe.DoesNotExistError)

	machine = frappe.get_doc("Printing Machine", name)
	context.machine = machine
	context.title = f"{machine.brand} {machine.model} | HamzaTraders"

	context.gallery = [row.image for row in machine.images if row.image] or [machine.thumbnail]

	capabilities = ", ".join(
		label
		for flag, label in (
			(machine.can_print, "Print"),
			(machine.can_scan, "Scan"),
			(machine.can_copy, "Copy"),
			(machine.can_fax, "Fax"),
		)
		if flag
	)

	context.spec_groups = [s for s in [
		{"label": "Machine Type", "value": machine.machine_type, "note": machine.tagline},
		{"label": "Capabilities", "value": capabilities, "note": None},
		{"label": "Print Technology", "value": machine.print_technology, "note": machine.print_resolution},
		{"label": "Print Speed", "value": machine.print_speed, "note": None},
		{"label": "Paper Handling", "value": machine.paper_sizes, "note": machine.paper_capacity},
		{
			"label": "Duplex / ADF",
			"value": ", ".join(
				v for v in (
					"Automatic Duplex" if machine.has_duplex else None,
					"Auto Document Feeder" if machine.has_adf else None,
				) if v
			),
			"note": None,
		},
		{"label": "Connectivity", "value": machine.connectivity, "note": None},
		{"label": "Scanner", "value": machine.scanner_resolution, "note": None},
		{"label": "Monthly Duty Cycle", "value": machine.monthly_duty_cycle, "note": None},
		{"label": "Memory", "value": machine.memory, "note": None},
		{"label": "Display / Control Panel", "value": machine.display_panel, "note": None},
		{"label": "Power", "value": machine.power_requirements, "note": None},
		{"label": "Dimensions", "value": machine.dimensions, "note": machine.weight},
		{
			"label": "Condition",
			"value": machine.condition,
			"note": machine.warranty,
		},
	] if s["value"]]

	context.assurances = [
		a for a in [
			{"icon": "truck", "label": machine.shipping_note},
			{"icon": "box", "label": machine.return_note},
			{"icon": "shield", "label": machine.warranty},
		]
		if a["label"]
	]

	context.compatible_accessories = _compatible_accessories(name)
	context.related = _related(machine)

	context.breadcrumbs = [
		{"label": "Home", "href": "/"},
		{"label": "Printing Machines", "href": "/printing-machines"},
		{"label": machine.brand, "href": f"/printing-machines?brand={machine.brand}"},
		{"label": machine.model, "href": None},
	]

	# ---- shell -------------------------------------------------------------
	context.page_bg = "bg-white"
	context.header_layout = "search-center"
	context.search_placeholder = "Search printing machines..."
	context.show_wishlist = False
	context.nav_items = [
		{"label": "Laptops", "href": "/shop"},
		{"label": "Accessories", "href": "/accessories"},
		{"label": "Printing Machines", "href": "/printing-machines", "active": True},
		{"label": "Printing Accessories", "href": "/printing-accessories"},
		{"label": "Support", "href": "/support"},
	]

	context.footer_variant = "full"
	context.footer_blurb = (
		"Your trusted destination for premium laptops, printers and accessories in Pakistan. "
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
	context.footer_note = "© 2024 HamzaTraders Pakistan. All rights reserved."

	return context


def _compatible_accessories(machine_name, limit=8):
	"""Reverse lookup: Printing Accessory rows whose `compatible_machines`
	child table links to this machine. The link only lives on the accessory
	side, so this is the one place it's queried in reverse."""
	names = frappe.get_all(
		"Printing Accessory Compatible Machine",
		filters={"machine": machine_name, "parenttype": "Printing Accessory"},
		pluck="parent",
		distinct=True,
	)
	if not names:
		return []
	return frappe.get_all(
		"Printing Accessory",
		filters={"name": ["in", names], "published": 1},
		fields=["name", "accessory_name", "brand", "slug", "tagline", "price", "image", "stock_status"],
		limit_page_length=limit,
	)


def _related(machine, limit=4):
	"""Comparable machines in a similar price band, across brands."""
	seen = {machine.name}
	picks = []

	def collect(filters):
		for row in frappe.get_all(
			"Printing Machine",
			filters=filters,
			fields=CARD_FIELDS,
			order_by="rating desc, review_count desc, creation desc",
			limit_page_length=limit * 3,
		):
			if row.name not in seen and len(picks) < limit:
				seen.add(row.name)
				picks.append(row)

	low, high = machine.price * 0.55, machine.price * 1.75
	collect({"published": 1, "price": ["between", [low, high]], "name": ["not in", list(seen)]})

	if len(picks) < limit:
		collect({"published": 1, "name": ["not in", list(seen)]})

	return picks[:limit]
