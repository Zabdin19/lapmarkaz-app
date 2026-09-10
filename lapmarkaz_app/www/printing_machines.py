# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Printing Machines listing: mirrors www/shop.py's filter architecture
against the Printing Machine doctype."""

from urllib.parse import urlencode

import frappe
from frappe.utils import cint, flt

PAGE_SIZE = 9

CARD_FIELDS = [
	"name",
	"brand",
	"model",
	"slug",
	"tagline",
	"condition",
	"show_condition_badge",
	"price",
	"compare_at_price",
	"thumbnail",
	"stock_status",
	"rating",
	"review_count",
	"machine_type",
	"print_technology",
	"color_mode",
	"is_multifunction",
	"is_new_arrival",
]

SORT_OPTIONS = [
	{"value": "latest", "label": "Latest", "order_by": "creation desc"},
	{"value": "price_asc", "label": "Price: Low to High", "order_by": "price asc"},
	{"value": "price_desc", "label": "Price: High to Low", "order_by": "price desc"},
	{"value": "rating", "label": "Top Rated", "order_by": "rating desc, review_count desc"},
	{"value": "name", "label": "Name A–Z", "order_by": "brand asc, model asc"},
]

# Query param -> Printing Machine fieldname. The three Check fields are
# rendered through the exact same facet machinery as everything else — their
# `_facet_options()` entry is just a fixed single "Yes" option instead of a
# list of distinct values, since shop.html's facet rendering is fully generic.
FACETS = [
	{"param": "brand", "field": "brand", "label": "Brand"},
	{"param": "machine_type", "field": "machine_type", "label": "Machine Type"},
	{"param": "condition", "field": "condition", "label": "Condition"},
	{"param": "color_mode", "field": "color_mode", "label": "Color / Monochrome"},
	{"param": "print_technology", "field": "print_technology", "label": "Print Technology"},
	{"param": "multifunction", "field": "is_multifunction", "label": "Multifunction"},
	{"param": "wifi", "field": "has_wifi", "label": "Wi-Fi"},
	{"param": "duplex", "field": "has_duplex", "label": "Duplex Printing"},
]

CHECK_FACETS = {"multifunction", "wifi", "duplex"}


def _selected():
	"""Multi-valued query params, e.g. ?brand=HP&brand=Canon."""
	args = getattr(frappe.request, "args", None)
	chosen = {}
	for facet in FACETS:
		values = args.getlist(facet["param"]) if args else []
		chosen[facet["param"]] = [v for v in values if v]
	return chosen


def _price_range():
	price_min = flt(frappe.form_dict.get("price_min")) or None
	price_max = flt(frappe.form_dict.get("price_max")) or None
	return price_min, price_max


def _facet_options():
	"""Build every facet's option list from what is actually published."""
	published = {"published": 1}

	def distinct(field):
		rows = frappe.get_all("Printing Machine", filters=published, fields=[field])
		return sorted({r[field] for r in rows if r[field] not in (None, "")})

	options = {
		"brand": [{"value": v, "label": v} for v in distinct("brand")],
		"machine_type": [{"value": v, "label": v} for v in distinct("machine_type")],
		"condition": [{"value": v, "label": v} for v in distinct("condition")],
		"color_mode": [{"value": v, "label": v} for v in distinct("color_mode")],
		"print_technology": [{"value": v, "label": v} for v in distinct("print_technology")],
	}
	for param, label in (
		("multifunction", "Multifunction only"),
		("wifi", "Wi-Fi enabled"),
		("duplex", "Duplex printing"),
	):
		options[param] = [{"value": "1", "label": label}]

	return options


def _build_filters(chosen, search, price_min=None, price_max=None):
	filters = [["Printing Machine", "published", "=", 1]]

	if price_min is not None:
		filters.append(["Printing Machine", "price", ">=", price_min])
	if price_max is not None:
		filters.append(["Printing Machine", "price", "<=", price_max])

	simple = {
		"brand": "brand",
		"machine_type": "machine_type",
		"condition": "condition",
		"color_mode": "color_mode",
		"print_technology": "print_technology",
	}
	for param, field in simple.items():
		if chosen.get(param):
			filters.append(["Printing Machine", field, "in", chosen[param]])

	check_fields = {"multifunction": "is_multifunction", "wifi": "has_wifi", "duplex": "has_duplex"}
	for param, field in check_fields.items():
		if chosen.get(param):
			filters.append(["Printing Machine", field, "=", 1])

	or_filters = []
	if search:
		like = f"%{search}%"
		or_filters = [
			["Printing Machine", "machine_name", "like", like],
			["Printing Machine", "brand", "like", like],
			["Printing Machine", "model", "like", like],
			["Printing Machine", "machine_type", "like", like],
			["Printing Machine", "tagline", "like", like],
		]

	return filters, or_filters


def _pagination(current, total_pages, window=2):
	if total_pages <= 1:
		return []

	pages = {1, total_pages}
	pages.update(range(max(1, current - window), min(total_pages, current + window) + 1))

	out, previous = [], 0
	for page in sorted(pages):
		if previous and page - previous > 1:
			out.append(None)
		out.append(page)
		previous = page
	return out


def get_context(context):
	context.no_cache = 1
	context.title = "Printing Machines | hamzatraders"

	chosen = _selected()
	search = (frappe.form_dict.get("q") or "").strip()
	sort = frappe.form_dict.get("sort") or "latest"
	view = frappe.form_dict.get("view") or "grid"
	page = max(cint(frappe.form_dict.get("page")) or 1, 1)
	price_min, price_max = _price_range()

	sort_option = next((s for s in SORT_OPTIONS if s["value"] == sort), SORT_OPTIONS[0])
	filters, or_filters = _build_filters(chosen, search, price_min, price_max)

	total = len(frappe.get_all("Printing Machine", filters=filters, or_filters=or_filters, pluck="name"))
	total_pages = max(-(-total // PAGE_SIZE), 1)
	page = min(page, total_pages)

	context.machines = frappe.get_all(
		"Printing Machine",
		filters=filters,
		or_filters=or_filters,
		fields=CARD_FIELDS,
		order_by=sort_option["order_by"],
		start=(page - 1) * PAGE_SIZE,
		page_length=PAGE_SIZE,
	)

	context.total = total
	context.page = page
	context.total_pages = total_pages
	context.page_numbers = _pagination(page, total_pages)
	context.facets = FACETS
	context.facet_options = _facet_options()
	context.selected = chosen
	context.search = search
	context.sort = sort_option["value"]
	context.sort_options = SORT_OPTIONS
	context.view = view
	context.active_filter_count = sum(len(v) for v in chosen.values())
	context.price_min = price_min
	context.price_max = price_max
	context.base_query = _base_query(chosen, search, sort, view, price_min, price_max)

	# ---- shell -------------------------------------------------------------
	context.page_bg = "bg-page"
	context.header_layout = "nav-left"
	context.search_placeholder = "Search printing machines..."
	context.nav_items = [
		{"label": "Laptops", "href": "/shop"},
		{"label": "Accessories", "href": "/accessories"},
		{"label": "Printing Machines", "href": "/printing-machines", "active": True},
		{"label": "Printing Accessories", "href": "/printing-accessories"},
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


def _base_query(chosen, search, sort, view, price_min=None, price_max=None):
	parts = [(param, value) for param, values in chosen.items() for value in values]

	if search:
		parts.append(("q", search))
	if sort and sort != "latest":
		parts.append(("sort", sort))
	if view and view != "grid":
		parts.append(("view", view))
	if price_min is not None:
		parts.append(("price_min", price_min))
	if price_max is not None:
		parts.append(("price_max", price_max))

	return urlencode(parts)
