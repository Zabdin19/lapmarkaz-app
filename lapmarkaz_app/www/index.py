# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Home page. Every section is driven by `Home Page Settings`; the carousel
reads Lapmarkaz Hero Slide, brands read Laptop Brand, use cases read Laptop
Usage, and the product rows read Laptop. Any section with nothing enabled to
show (no brands ticked, no testimonials, no FAQs, etc.) is left off the
context entirely so the template can skip it without rendering an empty
shell."""

from urllib.parse import urlencode

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
	context.title = settings.page_title or "HamzaTraders — Premium Tech for Pakistan"
	context.description = settings.meta_description or ""

	context.hero_slides = (
		frappe.get_all(
			"Lapmarkaz Hero Slide",
			filters={"published": 1},
			fields=[
				"eyebrow", "heading", "subheading", "cta_label", "cta_link",
				"secondary_cta_label", "secondary_cta_link", "image", "mobile_image",
			],
			order_by="display_order asc",
		)
		if settings.show_hero
		else []
	)

	context.value_props = _enabled(settings.value_props) if settings.show_value_props else []
	context.products = _products(SOURCES.get(settings.products_source or "New Arrivals"), settings.products_limit or 4)
	context.wishlist_ids = wishlisted_names()

	context.categories = _enabled(settings.home_categories) if settings.show_categories else []

	context.brands = (
		frappe.get_all(
			"Laptop Brand",
			filters={"show_on_home": 1},
			fields=["name", "brand_name", "logo"],
			order_by="display_order asc",
			limit_page_length=cint(settings.brands_limit) or 8,
		)
		if settings.show_brands
		else []
	)

	promo_rows = _enabled(settings.promo_banners)
	context.promo_primary = next((row for row in promo_rows if row.placement == "Primary"), None)
	context.promo_secondary = next((row for row in promo_rows if row.placement == "Secondary"), None)

	context.featured_products = (
		_products(SOURCES.get(settings.featured_source or "Featured"), settings.featured_limit or 4)
		if settings.show_featured
		else []
	)

	context.budget_ranges = (
		[
			{
				"title": row.title,
				"subtitle": row.subtitle,
				"link": _budget_link(row),
			}
			for row in _enabled(settings.budget_ranges)
		]
		if settings.show_budget
		else []
	)

	context.use_cases = (
		[
			{
				"name": row.name,
				"usage_name": row.usage_name,
				"image": row.image,
				"short_description": row.short_description,
				"link": f"/shop?{urlencode({'usage': row.usage_name})}",
			}
			for row in frappe.get_all(
				"Laptop Usage",
				filters={"show_on_home": 1},
				fields=["name", "usage_name", "image", "short_description"],
				order_by="display_order asc",
				limit_page_length=cint(settings.use_cases_limit) or 6,
			)
		]
		if settings.show_use_cases
		else []
	)

	context.why_choose_items = _enabled(settings.why_choose_items) if settings.show_why_choose else []
	context.testimonials = _enabled(settings.testimonials)
	context.faqs = _enabled(settings.faqs)

	context.update(storefront_chrome(active="/"))

	return context


def _enabled(rows):
	"""Child-table rows filtered to `enabled`, preserving their grid order."""
	return [row for row in rows if cint(row.get("enabled", 1))]


def _products(source, limit):
	if not source:
		source = SOURCES["New Arrivals"]
	extra, order_by = source
	return frappe.get_all(
		"Laptop",
		filters={"published": 1, **extra},
		fields=CARD_FIELDS,
		order_by=order_by,
		limit_page_length=cint(limit) or 4,
	)


def _budget_link(row):
	params = {}
	if row.min_price:
		params["price_min"] = cint(row.min_price)
	if row.max_price:
		params["price_max"] = cint(row.max_price)
	return f"/shop?{urlencode(params)}" if params else "/shop"
