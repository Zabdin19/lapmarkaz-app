# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Shared storefront chrome.

The header nav and the main footer are the same on the home page, the policy
pages and the store locator, so they all read from `Home Page Settings` rather
than repeating themselves in each controller.
"""

import frappe

from lapmarkaz_app.lapmarkaz.doctype.lapmarkaz_policy_page.lapmarkaz_policy_page import (
	customer_service_links,
)


def _settings():
	return frappe.get_cached_doc("Home Page Settings")


def storefront_nav(active=None):
	"""Nav items from Home Page Settings, with `active` marking the current page."""
	settings = _settings()
	brands = frappe.get_all(
		"Laptop Brand", fields=["name"], order_by="display_order asc", limit_page_length=8
	)

	items = []
	for row in settings.nav_items:
		href = row.link or "/"
		item = {"label": row.label, "href": href, "active": bool(active) and href == active}
		if row.brand_dropdown:
			item["dropdown"] = [{"label": b.name, "href": f"/shop?brand={b.name}"} for b in brands]
		items.append(item)
	return items


def storefront_header(active=None):
	settings = _settings()
	return {
		"header_layout": "search-left",
		"search_placeholder": settings.search_placeholder,
		"show_wishlist": bool(settings.show_wishlist),
		"nav_items": storefront_nav(active),
	}


def storefront_footer():
	settings = _settings()

	columns = {}
	for row in settings.footer_links:
		column = columns.setdefault(row.column_title, {"title": row.column_title, "links": []})
		column["links"].append({"label": row.label, "href": row.link or "/"})

	footer_columns = list(columns.values())
	if settings.show_policy_column:
		footer_columns.append(
			{
				"title": settings.policy_column_title or "Customer Service",
				"links": customer_service_links(),
			}
		)

	return {
		"footer_variant": "full",
		"footer_blurb": settings.footer_blurb,
		"footer_socials": [row.network for row in settings.socials],
		"footer_columns": footer_columns,
		"footer_contact": {
			"title": settings.contact_title,
			"address": settings.contact_address,
			"phone": settings.contact_phone,
			"email": settings.contact_email,
		},
		"footer_note": settings.footer_note,
	}


def storefront_chrome(active=None):
	"""Header + footer in one go."""
	return {**storefront_header(active), **storefront_footer()}
