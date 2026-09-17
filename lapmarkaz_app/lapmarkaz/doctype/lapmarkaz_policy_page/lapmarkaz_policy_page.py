# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class LapmarkazPolicyPage(WebsiteGenerator):
	website = frappe._dict(
		template="templates/generators/lapmarkaz_policy_page.html",
		condition_field="published",
		page_title_field="title",
	)

	def validate(self):
		if self.route:
			self.route = self.route.strip().strip("/")
		super().validate()

	def get_context(self, context):
		# Imported here, not at module level: chrome.py pulls
		# customer_service_links() from this module.
		from lapmarkaz_app.utils.chrome import storefront_chrome

		context.no_cache = 1
		page_title = self.meta_title or self.title
		for suffix in (" | Lapmarkaz", " | hamzatraders"):
			if page_title.endswith(suffix):
				page_title = page_title[: -len(suffix)]
		context.title = (
			page_title if page_title.endswith(" | HamzaTraders") else f"{page_title} | HamzaTraders"
		)
		context.description = self.meta_description or ""
		context.policy = self

		context.page_bg = "bg-white"
		context.update(storefront_chrome())
		return context


def customer_service_links():
	"""The footer's Customer Service column, driven by published policy pages.

	Shared with the home page so adding a policy page updates both.
	"""
	policies = frappe.get_all(
		"Lapmarkaz Policy Page",
		filters={"published": 1, "show_in_footer": 1},
		fields=["title", "route"],
		order_by="display_order asc",
	)

	return [{"label": p.title, "href": "/" + p.route} for p in policies] + [
		{"label": "Store Locator", "href": "/stores"}
	]
