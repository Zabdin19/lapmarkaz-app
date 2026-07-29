# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Store locator. Stores come from `Lapmarkaz Store`, page copy from
`Store Locator Settings`, header and footer from `Home Page Settings`."""

import frappe

from lapmarkaz_app.utils.chrome import storefront_chrome

FIELDS = [
	"name",
	"store_name",
	"city",
	"address",
	"phone",
	"email",
	"hours",
	"map_url",
	"is_flagship",
]


def get_context(context):
	context.no_cache = 1

	settings = frappe.get_cached_doc("Store Locator Settings")
	context.settings = settings
	context.title = settings.page_title or "Store Locator | Lapmarkaz"
	context.description = settings.meta_description or ""

	city = (frappe.form_dict.get("city") or "").strip()
	filters = {"published": 1}
	if city:
		filters["city"] = city

	context.stores = frappe.get_all(
		"Lapmarkaz Store",
		filters=filters,
		fields=FIELDS,
		order_by="is_flagship desc, display_order asc, store_name asc",
	)
	context.city = city
	context.cities = (
		frappe.get_all(
			"Lapmarkaz Store",
			filters={"published": 1},
			pluck="city",
			distinct=True,
			order_by="city asc",
		)
		if settings.show_city_filter
		else []
	)

	context.page_bg = "bg-page"
	context.update(storefront_chrome(active="/stores"))

	return context
