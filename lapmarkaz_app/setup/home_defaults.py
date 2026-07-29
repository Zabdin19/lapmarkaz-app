# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Populate Home Page Settings with the current home page content.

	bench --site site.localhost execute lapmarkaz_app.setup.home_defaults.run

This only provides the starting content — everything is editable afterwards
from Desk → Home Page Settings.
"""

import frappe

NAV = [
	("Home", "/", 0),
	("Shop", "/shop", 0),
	("Brands", "/shop", 1),
	("About Us", "/about", 0),
]

VALUE_PROPS = [
	("truck", "Fast Delivery (Karachi/Nationwide)"),
	("shield-check", "Easy Refund/Warranty"),
	("card", "Affordable Prices"),
	("payments", "Cash on Delivery"),
]

QUICK_LINKS = [
	("Quick Links", "Shop All", "/shop"),
	("Quick Links", "Brands", "/shop"),
	("Quick Links", "About Us", "/about"),
]

SOCIALS = [("facebook", "#"), ("youtube", "#"), ("twitter", "#")]


def run():
	settings = frappe.get_single("Home Page Settings")

	settings.update(
		{
			"search_placeholder": "Search for laptops, brands...",
			"show_wishlist": 1,
			"show_hero": 1,
			"show_value_props": 1,
			"products_heading": "New Arrivals",
			"products_subheading": "Latest models just added to our inventory.",
			"products_source": "New Arrivals",
			"products_cta_label": "View All",
			"products_cta_link": "/shop?sort=latest",
			"products_limit": 4,
			"show_newsletter": 1,
			"newsletter_heading": "Get Exclusive Deals",
			"newsletter_body": (
				"Subscribe to our newsletter to receive weekly updates on stock arrivals, "
				"exclusive discounts, and tech news."
			),
			"newsletter_placeholder": "Enter your email address",
			"newsletter_button_label": "Subscribe",
			"newsletter_success_message": "Thanks — you're on the list.",
			"footer_blurb": (
				"Premium laptop retailer in Pakistan. Offering authentic new and certified "
				"refurbished machines with warranty."
			),
			"show_policy_column": 1,
			"policy_column_title": "Customer Service",
			"contact_title": "Contact Us",
			"contact_address": "Karachi, Pakistan",
			"contact_phone": "+92 321 2789920",
			"contact_email": "Info@lapmarkaz.pk",
			"footer_note": "© 2024 Lapmarkaz Pakistan. All rights reserved.",
			"page_title": "Lapmarkaz — Premium Tech for Pakistan",
			"meta_description": (
				"Buy authentic new and certified refurbished laptops in Pakistan. Genuine "
				"warranty, nationwide delivery and cash on delivery."
			),
		}
	)

	settings.set("nav_items", [])
	for label, link, dropdown in NAV:
		settings.append("nav_items", {"label": label, "link": link, "brand_dropdown": dropdown})

	settings.set("value_props", [])
	for icon, title in VALUE_PROPS:
		settings.append("value_props", {"icon": icon, "title": title})

	settings.set("footer_links", [])
	for column_title, label, link in QUICK_LINKS:
		settings.append("footer_links", {"column_title": column_title, "label": label, "link": link})

	settings.set("socials", [])
	for network, url in SOCIALS:
		settings.append("socials", {"network": network, "url": url})

	settings.save(ignore_permissions=True)
	frappe.db.commit()

	print(
		f"Home Page Settings seeded: {len(NAV)} nav items, {len(VALUE_PROPS)} value props, "
		f"{len(QUICK_LINKS)} quick links, {len(SOCIALS)} socials."
	)
