# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Populate Home Page Settings with the current home page content.

	bench --site site.localhost execute lapmarkaz_app.setup.home_defaults.run

This only provides the starting content — everything is editable afterwards
from Desk → Home Page Settings.
"""

import frappe

IMG = "/assets/lapmarkaz_app/images/"

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

# Real, always-true destinations only — no invented categories.
HOME_CATEGORIES = [
	("New Laptops", "Brand new, full warranty", "/shop?condition=New", IMG + "laptop-silver.svg"),
	("Certified Refurbished", "Inspected & warrantied", "/shop?condition=Certified+Refurbished", IMG + "laptop-gray.svg"),
	("Accessories", "Bags, mice, chargers & more", "/accessories", IMG + "acc-backpack.svg"),
	("Printing Machines", "Laser, inkjet & multifunction", "/printing-machines", IMG + "cat-printer.svg"),
	("Printing Accessories", "Toner, ink, drums & parts", "/printing-accessories", IMG + "cat-cartridge.svg"),
]

# Two campaign slots (Primary = after New Arrivals, Secondary = lower on the
# page) — generic, always-true angles reusing claims already established on
# the About page, not invented offers/pricing.
PROMO_BANNERS = [
	{
		"placement": "Primary",
		"enabled": 1,
		"eyebrow": "QUALITY CHECKED",
		"heading": "Certified Refurbished Laptops",
		"description": "Every refurbished unit is inspected and comes backed by warranty — enterprise-grade machines at honest prices.",
		"cta_label": "Shop Refurbished",
		"cta_link": "/shop?condition=Certified+Refurbished",
		"desktop_image": IMG + "about-technician.svg",
		"layout": "Image Right",
	},
	{
		"placement": "Secondary",
		"enabled": 1,
		"eyebrow": "NOT SURE WHERE TO START?",
		"heading": "Need Help Choosing the Right Laptop?",
		"description": "Our team can help you find the right laptop for your budget, whether that's for study, work or gaming.",
		"cta_label": "Contact Us",
		"cta_link": "/support",
		"desktop_image": IMG + "about-store.svg",
		"layout": "Image Left",
	},
]

# Starter tiers the store owner suggested — meant to be tuned to actual
# catalog pricing from Desk, not treated as final.
BUDGET_RANGES = [
	("Under Rs. 40,000", 0, 40000, "Great for everyday tasks"),
	("Rs. 40,000 – 60,000", 40000, 60000, "Best value for students"),
	("Rs. 60,000 – 100,000", 60000, 100000, "Power for work & study"),
	("Rs. 100,000+", 100000, None, "Premium performance"),
]

# Short versions of the About page's already-published value copy
# (setup/about_defaults.py VALUES) plus the existing "Fast Delivery" claim —
# reused, not invented.
WHY_CHOOSE = [
	("award", "Quality Guaranteed", "Every laptop passes a rigorous inspection before it reaches our shelves."),
	("headset", "Unmatched Support", "Real warranty service and troubleshooting help after you buy."),
	("payments", "Transparent Pricing", "No hidden fees — fair prices for genuine premium tech."),
	("truck", "Nationwide Delivery", "Fast delivery across Karachi and the rest of Pakistan."),
]


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
			"show_categories": 1,
			"categories_heading": "Shop by Category",
			"categories_subheading": "Jump straight to what you're looking for.",
			"show_brands": 1,
			"brands_heading": "Shop Top Brands",
			"brands_subheading": "Authentic laptops from the brands you trust.",
			"brands_limit": 8,
			"show_featured": 1,
			"featured_heading": "Featured Laptops",
			"featured_subheading": "Hand-picked picks from our current inventory.",
			"featured_source": "Featured",
			"featured_cta_label": "View All",
			"featured_cta_link": "/shop",
			"featured_limit": 4,
			"show_budget": 1,
			"budget_heading": "Shop by Budget",
			"budget_subheading": "Find a laptop that fits what you want to spend.",
			"show_use_cases": 1,
			"use_cases_heading": "Shop by Use Case",
			"use_cases_subheading": "Pick a laptop for what you'll actually use it for.",
			"use_cases_limit": 6,
			"show_why_choose": 1,
			"why_choose_heading": "Why Choose hamzatraders",
			"testimonials_heading": "What Our Customers Say",
			"faq_heading": "Frequently Asked Questions",
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
			"footer_note": "© 2024 hamzatraders Pakistan. All rights reserved.",
			"page_title": "hamzatraders — Premium Tech for Pakistan",
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

	settings.set("home_categories", [])
	for title, subtitle, link, image in HOME_CATEGORIES:
		settings.append("home_categories", {"title": title, "subtitle": subtitle, "link": link, "image": image})

	settings.set("promo_banners", [])
	for row in PROMO_BANNERS:
		settings.append("promo_banners", row)

	settings.set("budget_ranges", [])
	for title, min_price, max_price, subtitle in BUDGET_RANGES:
		settings.append(
			"budget_ranges",
			{"title": title, "min_price": min_price, "max_price": max_price, "subtitle": subtitle},
		)

	settings.set("why_choose_items", [])
	for icon, title, description in WHY_CHOOSE:
		settings.append("why_choose_items", {"icon": icon, "title": title, "description": description})

	# Left empty on purpose: testimonials and faqs must never contain
	# placeholder/fake content — the admin adds real ones from Desk, and each
	# section stays hidden on the homepage until then.

	settings.save(ignore_permissions=True)
	frappe.db.commit()

	print(
		f"Home Page Settings seeded: {len(NAV)} nav items, {len(VALUE_PROPS)} value props, "
		f"{len(QUICK_LINKS)} quick links, {len(SOCIALS)} socials, {len(HOME_CATEGORIES)} categories, "
		f"{len(BUDGET_RANGES)} budget ranges, {len(WHY_CHOOSE)} why-choose items, "
		f"{len(PROMO_BANNERS)} promo banners. Testimonials and FAQs were left empty — add real ones from Desk."
	)
