# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Seed the policy pages and store locator.

	bench --site site.localhost execute lapmarkaz_app.setup.policy_defaults.run

Re-runnable. Every page is editable afterwards from the desk; adding a new
policy page is just a new Lapmarkaz Policy Page record with its own route.
"""

import frappe

PRIVACY = """
<h2>What we collect</h2>
<p>When you shop with hamzatraders we collect only what we need to fulfil your order: your name,
email address, phone number and delivery address. If you create an account we also store your
order history so you can look it up later.</p>
<p>We do not store card numbers. Card payments are handled by our payment partner and the card
details never reach our servers.</p>

<h2>How we use it</h2>
<ul>
<li>To process, verify and deliver your order</li>
<li>To contact you about an order, a warranty claim or a return</li>
<li>To send offers and stock updates, only if you opted in to our newsletter</li>
<li>To detect and prevent fraudulent orders</li>
</ul>

<h2>Who we share it with</h2>
<p>We share your name, address and phone number with the courier delivering your order. We never
sell your personal data, and we do not share it with advertisers.</p>

<h2>Cookies</h2>
<p>We use cookies to keep your cart between visits and to keep you signed in. Blocking cookies
will stop the cart from working.</p>

<h2>Your choices</h2>
<p>You can unsubscribe from marketing email at any time using the link in any newsletter. To
request a copy of your data or ask us to delete your account, email
<a href="mailto:Info@lapmarkaz.pk">Info@lapmarkaz.pk</a> and we will respond within seven
working days.</p>
"""

SHIPPING = """
<h2>Where we deliver</h2>
<p>We ship to every city in Pakistan through our courier partners. Orders are dispatched from our
Karachi warehouse once the verification call is complete.</p>

<h2>Delivery times</h2>
<ul>
<li><b>Karachi, Lahore, Islamabad</b> — 1 to 2 working days</li>
<li><b>Other major cities</b> — 3 to 4 working days</li>
<li><b>Remote areas</b> — 5 to 7 working days</li>
</ul>
<p>Orders placed after 4:00 PM, on Sundays or on public holidays are processed the next working
day.</p>

<h2>Shipping charges</h2>
<p>Delivery is <b>free on orders over Rs 20,000</b>. Below that a flat Rs 500 applies, shown at
checkout before you place the order.</p>

<h2>Verification call</h2>
<p>Every order gets a short confirmation call before dispatch. If we cannot reach you after three
attempts across two days, the order is placed on hold.</p>

<h2>Receiving your order</h2>
<p>Every laptop ships double-boxed with corner protection and is insured in transit. Please check
the packaging in front of the rider. If the box is visibly damaged, refuse the delivery and call
us the same day so we can send a replacement.</p>
"""

REFUND = """
<h2>7-day return window</h2>
<p>You have seven days from delivery to request a return for any reason. The laptop must be in the
condition it arrived in, with the charger, accessories and original packaging included.</p>

<h2>How to start a return</h2>
<ol>
<li>Email <a href="mailto:Info@lapmarkaz.pk">Info@lapmarkaz.pk</a> with your order number
and the reason for the return.</li>
<li>We arrange a courier pickup, usually within two working days.</li>
<li>Our technicians inspect the machine against the condition it was sold in.</li>
<li>We confirm the refund once the inspection passes.</li>
</ol>

<h2>Refund timelines</h2>
<ul>
<li><b>Cash on Delivery</b> — bank transfer within 5 to 7 working days of inspection</li>
<li><b>Card</b> — refunded to the original card within 7 to 10 working days</li>
<li><b>Easypaisa / JazzCash</b> — returned to the same wallet within 3 to 5 working days</li>
</ul>

<h2>What is not covered</h2>
<p>We cannot accept returns where the machine has physical or liquid damage caused after delivery,
where the serial number has been tampered with, or where accessories are missing. Software issues
and data loss are not grounds for a return — we are happy to help you troubleshoot instead.</p>

<h2>Faulty on arrival</h2>
<p>If a hardware fault appears within the first seven days we replace the unit outright rather
than repairing it, subject to stock. Beyond seven days your warranty applies.</p>
"""

POLICIES = [
	{
		"title": "Privacy Policy",
		"route": "privacy",
		"subtitle": "How hamzatraders collects, uses and protects the information you share with us.",
		"content": PRIVACY,
		"display_order": 1,
		"meta_description": "How hamzatraders collects, uses and protects your personal information.",
	},
	{
		"title": "Shipping Policy",
		"route": "shipping",
		"subtitle": "Delivery times, charges and what to expect once your order is on its way.",
		"content": SHIPPING,
		"display_order": 2,
		"meta_description": "hamzatraders delivery times, shipping charges and dispatch process across Pakistan.",
	},
	{
		"title": "Refund Policy",
		"route": "refunds",
		"subtitle": "Our 7-day return window, how to start a return, and when your money arrives.",
		"content": REFUND,
		"display_order": 3,
		"meta_description": "hamzatraders return window, refund timelines and what is covered.",
	},
]

STORES = [
	{
		"store_name": "hamzatraders Tech Mall",
		"city": "Karachi",
		"address": "Karachi, Pakistan",
		"phone": "+92 321 2789920",
		"email": "Info@lapmarkaz.pk",
		"hours": "Mon - Sat, 10:00 AM - 8:00 PM",
		"map_url": "https://maps.google.com/?q=hamzatraders+Karachi",
		"is_flagship": 1,
		"display_order": 1,
	},
	{
		"store_name": "hamzatraders Hall Road",
		"city": "Lahore",
		"address": "Office 4, Second Floor, Hafeez Centre, Gulberg III, Lahore",
		"phone": "+92 301 2345678",
		"email": "lahore@lapmarkaz.pk",
		"hours": "Mon - Sat, 11:00 AM - 8:00 PM",
		"map_url": "https://maps.google.com/?q=Hafeez+Centre+Lahore",
		"display_order": 2,
	},
	{
		"store_name": "hamzatraders Blue Area",
		"city": "Islamabad",
		"address": "Shop 22, Ground Floor, Jinnah Super Market, F-7 Markaz, Islamabad",
		"phone": "+92 302 3456789",
		"email": "islamabad@lapmarkaz.pk",
		"hours": "Mon - Sat, 11:00 AM - 8:00 PM",
		"map_url": "https://maps.google.com/?q=Jinnah+Super+Market+Islamabad",
		"display_order": 3,
	},
]


def _ensure(doctype, name, values):
	if frappe.db.exists(doctype, name):
		doc = frappe.get_doc(doctype, name)
		doc.update(values)
		doc.save(ignore_permissions=True)
		return doc

	doc = frappe.get_doc({"doctype": doctype, **values})
	doc.insert(ignore_permissions=True)
	return doc


def _ensure_policy(values):
	"""Keyed on `route`: WebsiteGenerator names the record from the scrubbed
	title, so the route is the stable identifier here."""
	existing = frappe.db.get_value("Lapmarkaz Policy Page", {"route": values["route"]}, "name")
	if existing:
		doc = frappe.get_doc("Lapmarkaz Policy Page", existing)
		doc.update(values)
		doc.save(ignore_permissions=True)
		return doc

	doc = frappe.get_doc({"doctype": "Lapmarkaz Policy Page", **values})
	doc.insert(ignore_permissions=True)
	return doc


def run():
	today = frappe.utils.nowdate()

	for policy in POLICIES:
		_ensure_policy({**policy, "published": 1, "show_in_footer": 1, "last_updated": today})

	for store in STORES:
		_ensure("Lapmarkaz Store", store["store_name"], {**store, "published": 1})

	settings = frappe.get_single("Store Locator Settings")
	settings.update(
		{
			"heading": "Find a HamzaTraders Store",
			"subheading": (
				"Come see the machines in person. Every branch keeps display stock you can test, "
				"and handles warranty drop-offs for orders bought online."
			),
			"show_city_filter": 1,
			"all_cities_label": "All cities",
			"flagship_label": "Flagship",
			"directions_label": "Get Directions",
			"empty_heading": "No stores listed here yet",
			"empty_body": "Try another city, or reach us online.",
			"empty_cta_label": "Contact Support",
			"empty_cta_link": "/support",
			"page_title": "Store Locator | HamzaTraders",
			"meta_description": "hamzatraders store addresses, phone numbers and opening hours across Pakistan.",
		}
	)
	settings.save(ignore_permissions=True)

	frappe.db.commit()
	print(f"Seeded {len(POLICIES)} policy pages and {len(STORES)} stores.")
