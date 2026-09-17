# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Support / help centre. All copy comes from `Support Page Settings`."""

import frappe


def get_context(context):
	context.no_cache = 1

	settings = frappe.get_cached_doc("Support Page Settings")
	context.settings = settings
	context.title = settings.page_title or "Support | HamzaTraders"
	context.description = settings.meta_description or ""

	search = (frappe.form_dict.get("q") or "").strip()
	context.search = search
	context.faqs = _match_faqs(settings.faqs, search)

	# ---- shell -------------------------------------------------------------
	context.page_bg = "bg-page"
	context.header_layout = "nav-center"
	context.hide_search = True
	context.account_first = True
	context.nav_items = [
		{"label": "Laptops", "href": "/shop"},
		{"label": "Accessories", "href": "/accessories"},
		{"label": "Support", "href": "/support", "active": True},
	]

	context.footer_variant = "light-split"
	context.footer_note = settings.footer_note
	context.footer_tagline = settings.footer_tagline
	context.footer_columns = _group_footer_links(settings.footer_links)

	return context


def _match_faqs(rows, search):
	"""The hero search box filters the FAQ list server-side."""
	if not search:
		return list(rows)

	needle = search.lower()
	return [r for r in rows if needle in (r.question or "").lower() or needle in (r.answer or "").lower()]


def _group_footer_links(rows):
	columns = {}
	for row in rows:
		column = columns.setdefault(row.column_title, {"title": row.column_title, "links": []})
		column["links"].append({"label": row.label, "href": row.link or "/"})
	return list(columns.values())
