# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Accessories listing. Filters query Lapmarkaz Accessory server-side; all page
copy comes from the `Accessories Page Settings` single."""

from urllib.parse import urlencode

import frappe
from frappe.utils import cint

from lapmarkaz_app.www.shop import _pagination

CARD_FIELDS = [
	"name",
	"accessory_name",
	"slug",
	"brand",
	"category",
	"connectivity",
	"tagline",
	"price",
	"image",
	"stock_status",
	"rating",
	"review_count",
	"is_best_seller",
]

SORT_OPTIONS = [
	{"value": "featured", "label": "Featured", "order_by": "is_featured desc, display_order asc"},
	{"value": "price_asc", "label": "Price: Low to High", "order_by": "price asc"},
	{"value": "price_desc", "label": "Price: High to Low", "order_by": "price desc"},
	{"value": "rating", "label": "Top Rated", "order_by": "rating desc, review_count desc"},
	{"value": "latest", "label": "Latest", "order_by": "creation desc"},
]

FACETS = [
	{"param": "category", "field": "category", "label": "Category"},
	{"param": "brand", "field": "brand", "label": "Brand"},
	{"param": "connectivity", "field": "connectivity", "label": "Connectivity"},
]

# The design spells the connectivity options out in full.
CONNECTIVITY_LABELS = {"Wireless": "Wireless (Bluetooth/2.4GHz)", "Wired": "Wired"}


def _selected():
	args = getattr(frappe.request, "args", None)
	return {
		facet["param"]: [v for v in (args.getlist(facet["param"]) if args else []) if v]
		for facet in FACETS
	}


def _facet_options():
	def ordered(doctype, order="display_order asc"):
		return frappe.get_all(doctype, pluck="name", order_by=order)

	return {
		"category": [{"value": v, "label": v} for v in ordered("Accessory Category")],
		"brand": [{"value": v, "label": v} for v in ordered("Accessory Brand")],
		"connectivity": [
			{"value": v, "label": CONNECTIVITY_LABELS[v]} for v in ("Wireless", "Wired")
		],
	}


def _build_filters(chosen, search):
	filters = [["Lapmarkaz Accessory", "published", "=", 1]]

	for facet in FACETS:
		values = chosen.get(facet["param"])
		if values:
			filters.append(["Lapmarkaz Accessory", facet["field"], "in", values])

	or_filters = []
	if search:
		like = f"%{search}%"
		or_filters = [
			["Lapmarkaz Accessory", "accessory_name", "like", like],
			["Lapmarkaz Accessory", "brand", "like", like],
			["Lapmarkaz Accessory", "category", "like", like],
			["Lapmarkaz Accessory", "tagline", "like", like],
		]

	return filters, or_filters


def get_context(context):
	context.no_cache = 1

	settings = frappe.get_cached_doc("Accessories Page Settings")
	context.settings = settings
	context.title = settings.page_title or "Premium Accessories | HamzaTraders"
	context.description = settings.meta_description or ""

	page_size = cint(settings.page_size) or 8
	chosen = _selected()
	search = (frappe.form_dict.get("q") or "").strip()
	sort = frappe.form_dict.get("sort") or "featured"
	page = max(cint(frappe.form_dict.get("page")) or 1, 1)

	sort_option = next((s for s in SORT_OPTIONS if s["value"] == sort), SORT_OPTIONS[0])
	filters, or_filters = _build_filters(chosen, search)

	total = len(
		frappe.get_all("Lapmarkaz Accessory", filters=filters, or_filters=or_filters, pluck="name")
	)
	total_pages = max(-(-total // page_size), 1)
	page = min(page, total_pages)

	context.accessories = frappe.get_all(
		"Lapmarkaz Accessory",
		filters=filters,
		or_filters=or_filters,
		fields=CARD_FIELDS,
		order_by=sort_option["order_by"],
		start=(page - 1) * page_size,
		page_length=page_size,
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
	context.hide_search = True
	context.accent_actions = True
	context.show_wishlist = True
	context.nav_items = [
		{"label": "Laptops", "href": "/shop"},
		{"label": "Accessories", "href": "/accessories", "active": True},
		{"label": "Printing Machines", "href": "/printing-machines"},
		{"label": "Printing Accessories", "href": "/printing-accessories"},
		{"label": "Support", "href": "/support"},
	]

	context.footer_variant = "dark-split"
	context.footer_tagline = settings.footer_tagline
	context.footer_links = [
		{"label": row.label, "href": row.link or "/"} for row in settings.footer_links
	]
	context.footer_note = settings.footer_note

	return context


def _base_query(chosen, search, sort):
	parts = [(param, value) for param, values in chosen.items() for value in values]
	if search:
		parts.append(("q", search))
	if sort and sort != "featured":
		parts.append(("sort", sort))
	return urlencode(parts)
