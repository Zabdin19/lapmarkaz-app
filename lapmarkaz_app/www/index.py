# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Home page. Every section is driven by `Home Page Settings`; the carousel
reads Lapmarkaz Hero Slide and the product row reads Laptop."""

import frappe
from frappe.utils import cint

from lapmarkaz_app.api.wishlist import wishlisted_names
from lapmarkaz_app.utils.chrome import storefront_chrome

CARD_FIELDS = [
	"name",
	"laptop_name",
	"brand",
	"model",
	"slug",
	"tagline",
	"condition",
	"grade",
	"price",
	"compare_at_price",
	"thumbnail",
	"stock_status",
	"is_new_arrival",
]

# Product section source -> (extra filters, order_by)
SOURCES = {
	"New Arrivals": ({"is_new_arrival": 1}, "creation asc"),
	"Featured": ({"is_featured": 1}, "creation asc"),
	"Best Sellers": ({"is_best_seller": 1}, "rating desc, review_count desc"),
	"Latest": ({}, "creation desc"),
	"Lowest Price": ({}, "price asc"),
}


def get_context(context):
	context.no_cache = 1

	settings = frappe.get_cached_doc("Home Page Settings")
	context.home = settings
	context.title = settings.page_title or "Lapmarkaz — Premium Tech for Pakistan"
	context.description = settings.meta_description or ""

	context.hero_slides = (
		frappe.get_all(
			"Lapmarkaz Hero Slide",
			filters={"published": 1},
			fields=["eyebrow", "heading", "subheading", "cta_label", "cta_link", "image"],
			order_by="display_order asc",
		)
		if settings.show_hero
		else []
	)

	context.products = _products(settings)
	context.value_props = settings.value_props if settings.show_value_props else []
	context.wishlist_ids = wishlisted_names()

	context.update(storefront_chrome(active="/"))

	return context


def _products(settings):
	extra, order_by = SOURCES.get(settings.products_source or "New Arrivals", SOURCES["New Arrivals"])
	return frappe.get_all(
		"Laptop",
		filters={"published": 1, **extra},
		fields=CARD_FIELDS,
		order_by=order_by,
		limit_page_length=cint(settings.products_limit) or 4,
	)


