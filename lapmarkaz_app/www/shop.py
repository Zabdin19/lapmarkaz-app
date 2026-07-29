# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Shop listing: every filter here queries the Laptop table server-side."""

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
	"grade",
	"show_condition_badge",
	"price",
	"compare_at_price",
	"thumbnail",
	"stock_status",
	"rating",
	"review_count",
	"processor",
	"ram_gb",
	"storage",
	"screen_size",
]

SORT_OPTIONS = [
	{"value": "latest", "label": "Latest", "order_by": "creation desc"},
	{"value": "price_asc", "label": "Price: Low to High", "order_by": "price asc"},
	{"value": "price_desc", "label": "Price: High to Low", "order_by": "price desc"},
	{"value": "rating", "label": "Top Rated", "order_by": "rating desc, review_count desc"},
	{"value": "name", "label": "Name A–Z", "order_by": "brand asc, model asc"},
]

# Query param -> Laptop fieldname. `usage` is handled separately (child table).
FACETS = [
	{"param": "condition", "field": "condition", "label": "Condition"},
	{"param": "usage", "field": None, "label": "Usage"},
	{"param": "brand", "field": "brand", "label": "Brand"},
	{"param": "model", "field": "model", "label": "Model"},
	{"param": "processor", "field": "processor_family", "label": "Processor"},
	{"param": "generation", "field": "generation", "label": "Generation"},
	{"param": "ram", "field": "ram_gb", "label": "RAM"},
	{"param": "screen", "field": "screen_size", "label": "Screen Size"},
]


def _selected():
	"""Multi-valued query params, e.g. ?brand=HP&brand=Dell."""
	args = getattr(frappe.request, "args", None)
	chosen = {}
	for facet in FACETS:
		values = args.getlist(facet["param"]) if args else []
		chosen[facet["param"]] = [v for v in values if v]
	return chosen


def _facet_options():
	"""Build every facet's option list from what is actually published."""
	published = {"published": 1}

	def distinct(field):
		# Deduped in Python: some of these fieldnames (`condition`) are SQL
		# reserved words that Frappe does not quote in GROUP BY / ORDER BY.
		rows = frappe.get_all("Laptop", filters=published, fields=[field])
		return sorted({r[field] for r in rows if r[field] not in (None, "")})

	usages = frappe.get_all("Laptop Usage", pluck="name", order_by="name asc")

	options = {
		"condition": [{"value": v, "label": v} for v in distinct("condition")],
		"usage": [{"value": v, "label": v} for v in usages],
		"brand": [{"value": v, "label": v} for v in distinct("brand")],
		"model": [{"value": v, "label": v} for v in distinct("model")],
		"processor": [{"value": v, "label": v} for v in distinct("processor_family")],
		"generation": [{"value": v, "label": v} for v in distinct("generation")],
		"ram": [{"value": str(cint(v)), "label": f"{cint(v)}GB"} for v in distinct("ram_gb")],
		"screen": [{"value": str(flt(v)), "label": f'{flt(v):g}"'} for v in distinct("screen_size")],
	}

	# Generations sort better by their leading number than alphabetically.
	options["generation"].sort(key=lambda o: (o["value"] == "M Series", cint(o["value"].split("th")[0] or 0)))
	options["ram"].sort(key=lambda o: cint(o["value"]))
	options["screen"].sort(key=lambda o: flt(o["value"]))
	return options


def _build_filters(chosen, search):
	filters = [["Laptop", "published", "=", 1]]

	simple = {
		"condition": "condition",
		"brand": "brand",
		"model": "model",
		"processor": "processor_family",
		"generation": "generation",
	}
	for param, field in simple.items():
		if chosen.get(param):
			filters.append(["Laptop", field, "in", chosen[param]])

	if chosen.get("ram"):
		filters.append(["Laptop", "ram_gb", "in", [cint(v) for v in chosen["ram"]]])

	if chosen.get("screen"):
		filters.append(["Laptop", "screen_size", "in", [flt(v) for v in chosen["screen"]]])

	if chosen.get("usage"):
		# Resolve the child table to a set of parents, then filter on it.
		parents = frappe.get_all(
			"Laptop Usage Item",
			filters={"usage": ["in", chosen["usage"]], "parenttype": "Laptop"},
			pluck="parent",
			distinct=True,
		)
		filters.append(["Laptop", "name", "in", parents or [""]])

	or_filters = []
	if search:
		like = f"%{search}%"
		or_filters = [
			["Laptop", "laptop_name", "like", like],
			["Laptop", "brand", "like", like],
			["Laptop", "model", "like", like],
			["Laptop", "processor", "like", like],
			["Laptop", "tagline", "like", like],
		]

	return filters, or_filters


def _pagination(current, total_pages, window=2):
	"""Page numbers plus `None` markers where an ellipsis belongs."""
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
	context.title = "All Laptops | Lapmarkaz"

	chosen = _selected()
	search = (frappe.form_dict.get("q") or "").strip()
	sort = frappe.form_dict.get("sort") or "latest"
	view = frappe.form_dict.get("view") or "grid"
	page = max(cint(frappe.form_dict.get("page")) or 1, 1)

	sort_option = next((s for s in SORT_OPTIONS if s["value"] == sort), SORT_OPTIONS[0])
	filters, or_filters = _build_filters(chosen, search)

	total = len(frappe.get_all("Laptop", filters=filters, or_filters=or_filters, pluck="name"))
	total_pages = max(-(-total // PAGE_SIZE), 1)
	page = min(page, total_pages)

	context.laptops = frappe.get_all(
		"Laptop",
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
	context.base_query = _base_query(chosen, search, sort, view)

	# ---- shell -------------------------------------------------------------
	context.page_bg = "bg-page"
	context.header_layout = "nav-left"
	context.search_placeholder = "Search products..."
	context.nav_items = [
		{"label": "Laptops", "href": "/shop", "active": True},
		{"label": "Accessories", "href": "/accessories"},
		{"label": "Support", "href": "/support"},
	]
	context.footer_variant = "slim"
	context.footer_note = "© 2024 Lapmarkaz. Premium Tech for Pakistan."
	context.footer_links = [
		{"label": "Warranty Policy", "href": "/warranty"},
		{"label": "Shipping Info", "href": "/shipping"},
		{"label": "Privacy", "href": "/privacy"},
		{"label": "Terms of Service", "href": "/terms"},
	]

	return context


def _base_query(chosen, search, sort, view):
	"""Everything except `page`, so pagination links can just append it."""
	parts = [(param, value) for param, values in chosen.items() for value in values]

	if search:
		parts.append(("q", search))
	if sort and sort != "latest":
		parts.append(("sort", sort))
	if view and view != "grid":
		parts.append(("view", view))

	return urlencode(parts)
