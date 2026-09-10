# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Populate Support Page Settings with the launch copy.

	bench --site site.localhost execute lapmarkaz_app.setup.support_defaults.run
"""

import frappe

CATEGORIES = [
	("truck", "Orders & Shipping", "Track your order, shipping policies, and delivery times.", "/track"),
	("verified", "Warranty & Repairs", "Warranty terms, claim process, and authorized service centers.", "/warranty"),
	("headset", "Technical Support", "Troubleshooting, drivers, and software assistance.", "/support?q=driver"),
	("refresh", "Returns & Refunds", "Return policies, refund status, and exchange procedures.", "/refunds"),
]

FAQS = [
	(
		"How do I track my order?",
		"Once your order is confirmed you'll get an SMS and email with a tracking link. You can also "
		"open the confirmation page from your order email at any time to see the current status and "
		"expected delivery date.",
	),
	(
		"What is the warranty policy for refurbished laptops?",
		"Every certified refurbished laptop ships with a one-month hamzatraders warranty covering "
		"hardware faults. Machines listed as New carry a full one-year warranty. Physical damage, "
		"liquid damage and consumables are not covered.",
	),
	(
		"Do you offer cash on delivery?",
		"Yes. Cash on Delivery is available nationwide. We call to verify every order before "
		"dispatch, and you can inspect the packaging before paying the rider.",
	),
	(
		"How long does delivery take?",
		"Karachi, Lahore and Islamabad usually receive orders within 2 working days. Other cities "
		"take 3 to 5 working days. Shipping is free on orders over Rs 20,000.",
	),
	(
		"Can I return a laptop if I change my mind?",
		"You have 7 days from delivery to request a return. The machine must be in the condition it "
		"arrived in, with all accessories and the original packaging.",
	),
]

CHANNELS = [
	("mail", "Email Support", "Info@lapmarkaz.pk", "mailto:Info@lapmarkaz.pk"),
	("message", "WhatsApp", "+92 321 2789920", "https://wa.me/923212789920"),
	("clock", "Business Hours", "Mon - Sat, 10:00 AM - 6:00 PM (PKT)", ""),
]

RESOURCES = [
	("download", "Download Drivers", "/drivers"),
	("book", "User Manuals", "/manuals"),
	("clipboard-check", "Verify Warranty", "/warranty"),
]

FOOTER_LINKS = [
	("Company", "About Us", "/about"),
	("Company", "Contact Us", "/contact"),
	("Policies", "Privacy Policy", "/privacy"),
	("Policies", "Shipping Policy", "/shipping"),
	("More", "Returns", "/refunds"),
	("More", "Terms of Service", "/terms"),
]


def run():
	settings = frappe.get_single("Support Page Settings")

	settings.update(
		{
			"hero_heading": "How can we help you today?",
			"hero_subheading": (
				"Search our knowledge base or browse categories below to find answers to your questions."
			),
			"search_placeholder": "Search for help...",
			"show_search": 1,
			"categories_heading": "Help Categories",
			"faq_heading": "Frequently Asked Questions",
			"contact_heading": "Contact Us",
			"contact_button_label": "Send Message",
			"contact_success_message": (
				"Thanks — we've got your message and will reply within one business day."
			),
			"channels_heading": "Direct Channels",
			"resources_heading": "Technical Resources",
			"footer_note": "© 2024 hamzatraders. All rights reserved.",
			"footer_tagline": "Premium Laptops in Pakistan.",
			"page_title": "Support | hamzatraders",
			"meta_description": (
				"Track orders, claim warranty, download drivers or talk to the hamzatraders team. "
				"Answers to the questions we're asked most."
			),
		}
	)

	settings.set("categories", [])
	for icon, title, description, link in CATEGORIES:
		settings.append(
			"categories", {"icon": icon, "title": title, "description": description, "link": link}
		)

	settings.set("faqs", [])
	for question, answer in FAQS:
		settings.append("faqs", {"question": question, "answer": answer})

	settings.set("channels", [])
	for icon, label, value, link in CHANNELS:
		settings.append("channels", {"icon": icon, "label": label, "value": value, "link": link})

	settings.set("resources", [])
	for icon, title, link in RESOURCES:
		settings.append("resources", {"icon": icon, "title": title, "link": link})

	settings.set("footer_links", [])
	for column_title, label, link in FOOTER_LINKS:
		settings.append("footer_links", {"column_title": column_title, "label": label, "link": link})

	settings.save(ignore_permissions=True)
	frappe.db.commit()

	print(
		f"Support Page Settings seeded: {len(CATEGORIES)} categories, {len(FAQS)} FAQs, "
		f"{len(CHANNELS)} channels, {len(RESOURCES)} resources."
	)
