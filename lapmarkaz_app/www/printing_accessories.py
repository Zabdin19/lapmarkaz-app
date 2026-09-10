# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Printing Accessories listing. Mirrors www/accessories.py's filter
architecture against the Printing Accessory doctype."""

from urllib.parse import urlencode

import frappe
from frappe.utils import cint

from lapmarkaz_app.www.shop import _pagination

CARD_FIELDS = [
	"name",
	"accessory_name",
	"slug",
	"brand",
	"accessory_type",
	"tagline",
	"price",
	"compare_at_price",
	"image",
	"stock_status",
	"rating",
	"review_count",
	"is_featured",
	"is_new_arrival",
]

SORT_OPTIONS = [
	{"value": "featured", "label": "Featured", "order_by": "is_featured desc, creation desc"},
	{"value": "price_asc", "label": "Price: Low to High", "order_by": "price asc"},
	{"value": "price_desc", "label": "Price: High to Low", "order_by": "price desc"},
	{"value": "rating", "label": "Top Rated", "order_by": "rating desc, review_count desc"},
	{"value": "latest", "label": "Latest", "order_by": "creation desc"},
]

FACETS = [
	{"param": "brand", "field": "brand", "label": "Brand"},
	{"param": "type", "field": "accessory_type", "label": "Type"},
]

PAGE_SIZE = 8


def _selected():
	args = getattr(frappe.request, "args", None)
	return {
		facet["param"]: [v for v in (args.getlist(facet["param"]) if args else []) if v]
		for facet in FACETS
	}


def _facet_options():
	return {
		"brand": [{"value": v, "label": v} for v in frappe.get_all(
			"Printing Brand", pluck="name", order_by="display_order asc"
		)],
		"type": [{"value": v, "label": v} for v in frappe.get_all(
			"Printing Accessory Type", pluck="name", order_by="display_order asc"
		)],
	}


def _build_filters(chosen, search):
	filters = [["Printing Accessory", "published", "=", 1]]

	if chosen.get("brand"):
		filters.append(["Printing Accessory", "brand", "in", chosen["brand"]])
	if chosen.get("type"):
		filters.append(["Printing Accessory", "accessory_type", "in", chosen["type"]])

	or_filters = []
	if search:
		like = f"%{search}%"
		or_filters = [
			["Printing Accessory", "accessory_name", "like", like],
			["Printing Accessory", "brand", "like", like],
			["Printing Accessory", "accessory_type", "like", like],
			["Printing Accessory", "tagline", "like", like],
		]

	return filters, or_filters


def get_context(context):
	context.no_cache = 1
	context.title = "Printing Accessories | hamzatraders"
	context.heading = "Printing Accessories"
	context.subheading = "Toner, ink, drums and parts for your printer — filter by brand or type below."

	chosen = _selected()
	search = (frappe.form_dict.get("q") or "").strip()
	sort = frappe.form_dict.get("sort") or "featured"
	page = max(cint(frappe.form_dict.get("page")) or 1, 1)

	sort_option = next((s for s in SORT_OPTIONS if s["value"] == sort), SORT_OPTIONS[0])
	filters, or_filters = _build_filters(chosen, search)

	total = len(
		frappe.get_all("Printing Accessory", filters=filters, or_filters=or_filters, pluck="name")
	)
	total_pages = max(-(-total // PAGE_SIZE), 1)
	page = min(page, total_pages)

	context.accessories = frappe.get_all(
		"Printing Accessory",
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
	context.active_filter_count = sum(len(v) for v in chosen.values())
	context.base_query = _base_query(chosen, search, sort)

	# ---- shell -------------------------------------------------------------
	context.page_bg = "bg-page"
	context.header_layout = "nav-left"
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


def _base_query(chosen, search, sort):
	parts = [(param, value) for param, values in chosen.items() for value in values]
	if search:
		parts.append(("q", search))
	if sort and sort != "featured":
		parts.append(("sort", sort))
	return urlencode(parts)
