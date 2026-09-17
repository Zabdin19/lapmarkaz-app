# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Populate About Page Settings with the launch copy.

	bench --site site.localhost execute lapmarkaz_app.setup.about_defaults.run

Everything written here is editable afterwards from the desk — this only
provides the starting content so the page isn't blank.
"""

import frappe

IMG = "/assets/lapmarkaz_app/images/"

VALUES = [
	(
		"award",
		"Quality Guaranteed",
		"Every laptop undergoes a rigorous 50-point inspection process by our certified "
		"technicians before it reaches our shelves, ensuring peak performance.",
	),
	(
		"headset",
		"Unmatched Support",
		"Our dedicated technical support team is available to assist you post-purchase, "
		"offering comprehensive warranty services and troubleshooting guidance.",
	),
	(
		"payments",
		"Transparent Pricing",
		"No hidden fees, no deceptive markups. We believe in offering fair, competitive "
		"prices that reflect the true value of premium technology in the local market.",
	),
]

TRUST = [
	("check-circle", "Genuine Warranty"),
	("truck", "Fast Delivery"),
	("lock", "Secure Payment"),
]

TAGS = ["Lenovo ThinkPad", "HP EliteBook", "Dell XPS", "Apple MacBook"]

FOOTER_LINKS = [
	("Support", "Privacy Policy", "/privacy"),
	("Support", "Shipping Policy", "/shipping"),
	("Support", "Refund Policy", "/refunds"),
	("Company", "About Us", "/about"),
	("Company", "Store Locator", "/stores"),
	("Company", "Contact Us", "/contact"),
]


def run():
	settings = frappe.get_single("About Page Settings")

	settings.update(
		{
			"hero_heading": "Empowering Pakistan with Premium Tech",
			"hero_body": (
				"At hamzatraders, our mission is to provide authentic, high-quality laptops and "
				"accessories that empower students, professionals, and creators across Pakistan. "
				"We bridge the gap between premium global tech and local accessibility."
			),
			"hero_cta_label": "Shop Now",
			"hero_cta_link": "/shop",
			"hero_image": IMG + "about-office.svg",
			"story_heading": "Our Story",
			"story_body": (
				"hamzatraders started with a simple observation: the tech market in Pakistan suffered "
				"from a massive trust gap. Customers struggled to distinguish between genuinely "
				"refurbished premium laptops and low-quality imports. We founded hamzatraders to bring "
				"transparency, rigorous quality control, and exceptional customer support to the "
				"local tech landscape, ensuring every purchase is a secure investment in your future."
			),
			"values_heading": "Our Core Values",
			"expertise_heading": "Our Expertise",
			"expertise_body": (
				"We specialize in certified refurbished processes that restore premium tech devices "
				"to factory standards. By partnering with leading global brands, we curate an "
				"inventory tailored to professional and creative demands."
			),
			"expertise_image_1": IMG + "about-technician.svg",
			"expertise_image_2": IMG + "about-store.svg",
			"cta_heading": "Experience the hamzatraders Difference",
			"cta_body": (
				"Join thousands of satisfied professionals and students who have upgraded their "
				"tech journey with our premium, reliable laptops."
			),
			"cta_label": "Explore the Shop",
			"cta_link": "/shop",
			"show_trust_strip": 1,
			"footer_tagline": "Premium tech solutions for Pakistan. Quality guaranteed.",
			"contact_email": "Info@lapmarkaz.pk",
			"contact_phone": "+92 321 2789920",
			"footer_note": "© 2024 HamzaTraders Pakistan. All rights reserved.",
			"page_title": "About Us | HamzaTraders",
			"meta_description": (
				"hamzatraders provides authentic, certified refurbished laptops and accessories "
				"across Pakistan, backed by rigorous inspection and real warranty support."
			),
		}
	)

	settings.set("values", [])
	for icon, title, description in VALUES:
		settings.append("values", {"icon": icon, "title": title, "description": description})

	settings.set("trust_items", [])
	for icon, title in TRUST:
		settings.append("trust_items", {"icon": icon, "title": title})

	settings.set("expertise_tags", [])
	for label in TAGS:
		settings.append("expertise_tags", {"label": label})

	settings.set("footer_links", [])
	for column_title, label, link in FOOTER_LINKS:
		settings.append("footer_links", {"column_title": column_title, "label": label, "link": link})

	settings.save(ignore_permissions=True)
	frappe.db.commit()

	print(
		f"About Page Settings seeded: {len(VALUES)} values, {len(TAGS)} tags, "
		f"{len(FOOTER_LINKS)} footer links."
	)
