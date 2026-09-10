# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Seed the accessories catalogue and the /accessories page copy.

	bench --site site.localhost execute lapmarkaz_app.setup.accessories_data.run

Re-runnable: existing records are updated in place.
"""

import frappe

IMG = "/assets/lapmarkaz_app/images/"

CATEGORIES = ["Mice", "Keyboards", "Chargers & Adapters", "Bags & Sleeves", "Headsets"]
BRANDS = ["Logitech", "Razer", "Dell", "HP", "Lenovo", "Anker", "Corsair", "hamzatraders Essentials"]

# Category -> placeholder artwork, with a few per-product overrides.
ART = {
	"Mice": IMG + "acc-mouse.svg",
	"Keyboards": IMG + "acc-keyboard.svg",
	"Chargers & Adapters": IMG + "acc-charger.svg",
	"Bags & Sleeves": IMG + "acc-sleeve.svg",
	"Headsets": IMG + "acc-headset.svg",
}

ART_OVERRIDES = {
	"ThinkPad Professional Backpack": IMG + "acc-backpack.svg",
	"Premium Laptop Backpack": IMG + "acc-backpack.svg",
	"7-in-1 USB-C Hub": IMG + "acc-hub.svg",
	"Dual Fan Cooling Pad": IMG + "acc-cooling-pad.svg",
}

# Dropped when the accessory catalogue moved out of setup/demo_data.py.
RETIRED = ["Ergonomic Wireless Mouse"]

# fmt: off
# name | brand | category | connectivity | price | rating | reviews | tagline | flags
CATALOGUE = [
	("MX Master 3S Wireless Performance Mouse", "Logitech", "Mice", "Wireless", 32500, 4.9, 128, "8K DPI, quiet clicks, USB-C", "best,featured"),
	("DeathAdder V3 Pro Wireless Gaming Mouse", "Razer", "Mice", "Wireless", 45000, 4.8, 85, "63g, 30K DPI optical sensor", "featured"),
	("65W Type-C AC Power Adapter", "Dell", "Chargers & Adapters", "Wired", 12500, 4.6, 214, "Slim tip, 1.8m cable", "featured"),
	('Premium Water-Resistant 15.6" Laptop Sleeve', "hamzatraders Essentials", "Bags & Sleeves", "", 4200, 4.7, 56, "Fleece lined, splash proof", "featured"),
	("MX Keys S Wireless Keyboard", "Logitech", "Keyboards", "Wireless", 28500, 4.8, 97, "Backlit, low profile, multi-device", "best"),
	("BlackWidow V4 Mechanical Keyboard", "Razer", "Keyboards", "Wired", 38000, 4.7, 63, "Green switches, per-key RGB", ""),
	("Barracuda X Wireless Headset", "Razer", "Headsets", "Wireless", 26500, 4.5, 74, "2.4GHz + Bluetooth, 50h battery", ""),
	("Zone Vibe 100 Lightweight Headset", "Logitech", "Headsets", "Wireless", 19500, 4.4, 41, "Noise-reducing mic, 20h battery", ""),
	("Pebble M350 Silent Wireless Mouse", "Logitech", "Mice", "Wireless", 6500, 4.6, 188, "Slim, silent click, 18-month battery", ""),
	("Basilisk V3 Ergonomic Mouse", "Razer", "Mice", "Wired", 17500, 4.7, 92, "11 programmable buttons", ""),
	("MK270 Wireless Keyboard & Mouse Combo", "Logitech", "Keyboards", "Wireless", 9800, 4.3, 246, "Full-size layout, 3-year battery", ""),
	("K120 Wired Business Keyboard", "Logitech", "Keyboards", "Wired", 3200, 4.2, 310, "Spill resistant, plug and play", ""),
	("K95 RGB Platinum Mechanical Keyboard", "Corsair", "Keyboards", "Wired", 52000, 4.8, 38, "Cherry MX, aluminium frame", ""),
	("90W Smart AC Adapter", "HP", "Chargers & Adapters", "Wired", 9800, 4.4, 132, "Blue tip, surge protected", ""),
	("65W USB-C Slim Travel Charger", "Lenovo", "Chargers & Adapters", "Wired", 11200, 4.5, 87, "GaN, foldable pins", ""),
	("735 Pro GaN 100W Charger", "Anker", "Chargers & Adapters", "Wired", 15500, 4.8, 164, "3 ports, charges laptop + phone", "best"),
	("7-in-1 USB-C Hub", "Anker", "Chargers & Adapters", "Wired", 4200, 4.5, 203, "HDMI, USB 3.0, SD Card", ""),
	("ThinkPad Professional Backpack", "Lenovo", "Bags & Sleeves", "", 8900, 4.6, 71, 'Fits up to 15.6", padded', ""),
	("Premium Laptop Backpack", "hamzatraders Essentials", "Bags & Sleeves", "", 3500, 4.3, 149, 'Fits up to 15.6"', ""),
	('Renew Business 14" Sleeve', "HP", "Bags & Sleeves", "", 5600, 4.4, 44, "Recycled fabric, slim profile", ""),
	("Dual Fan Cooling Pad", "hamzatraders Essentials", "Bags & Sleeves", "Wired", 2100, 4.1, 96, 'For up to 17" Laptops', ""),
	("Pro X 2 Lightspeed Gaming Headset", "Logitech", "Headsets", "Wireless", 61000, 4.9, 52, "Graphene drivers, 50h battery", "best"),
	("HS80 RGB Wireless Headset", "Corsair", "Headsets", "Wireless", 34500, 4.6, 67, "Broadcast-grade mic, Dolby Atmos", ""),
	("Pro Stereo Wired Headset", "Dell", "Headsets", "Wired", 8400, 4.2, 118, "Inline controls, noise-cancelling mic", ""),
]
# fmt: on

FEATURES = [
	("verified", "Genuine Warranty", "Official local and international warranties on all accessories."),
	("truck", "Fast Delivery", "Nationwide express shipping across Pakistan."),
	("lock", "Secure Payment", "Multiple safe payment options including Cash on Delivery."),
]

FOOTER_LINKS = [
	("Accessories", "About Us", "/about"),
	("Accessories", "Contact Us", "/contact"),
	("Accessories", "Privacy Policy", "/privacy"),
	("Accessories", "Terms of Service", "/terms"),
	("Accessories", "Corporate Sales", "/corporate"),
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


def run():
	for name in RETIRED:
		if frappe.db.exists("Lapmarkaz Accessory", name):
			frappe.delete_doc("Lapmarkaz Accessory", name, force=1, ignore_permissions=True)

	for i, category in enumerate(CATEGORIES):
		_ensure("Accessory Category", category, {"category_name": category, "display_order": i + 1})

	for i, brand in enumerate(BRANDS):
		_ensure("Accessory Brand", brand, {"brand_name": brand, "display_order": i + 1})

	for i, row in enumerate(CATALOGUE):
		name, brand, category, connectivity, price, rating, reviews, tagline, flags = row
		flags = flags.split(",") if flags else []

		_ensure(
			"Lapmarkaz Accessory",
			name,
			{
				"accessory_name": name,
				"slug": frappe.scrub(name).replace("_", "-"),
				"brand": brand,
				"category": category,
				"connectivity": connectivity or None,
				"tagline": tagline,
				"price": price,
				"rating": rating,
				"review_count": reviews,
				"image": ART_OVERRIDES.get(name, ART[category]),
				"stock_status": "In Stock",
				"published": 1,
				"display_order": i + 1,
				"is_best_seller": 1 if "best" in flags else 0,
				"is_featured": 1 if "featured" in flags else 0,
				"description": (
					f"<p>The <b>{brand} {name}</b> — {tagline}.</p>"
					"<p>Sourced through official channels and covered by our standard warranty. "
					"Ships free with any laptop order.</p>"
				),
			},
		)

	settings = frappe.get_single("Accessories Page Settings")
	settings.update(
		{
			"heading": "Premium Accessories",
			"subheading": (
				"Enhance your computing experience with our curated selection of high-performance "
				"peripherals, from ergonomic mice to professional-grade audio gear."
			),
			"show_features": 1,
			"footer_tagline": (
				"High-performance computing for Pakistan. Your trusted source for premium "
				"laptops and accessories."
			),
			"footer_note": "© 2024 hamzatraders. All rights reserved. High-performance computing for Pakistan.",
			"page_title": "Premium Accessories | hamzatraders",
			"meta_description": (
				"Shop mice, keyboards, chargers, bags and headsets from Logitech, Razer, Dell, "
				"HP and Lenovo — with genuine warranty and nationwide delivery."
			),
			"page_size": 8,
		}
	)

	settings.set("features", [])
	for icon, title, description in FEATURES:
		settings.append("features", {"icon": icon, "title": title, "description": description})

	settings.set("footer_links", [])
	for column_title, label, link in FOOTER_LINKS:
		settings.append("footer_links", {"column_title": column_title, "label": label, "link": link})

	settings.save(ignore_permissions=True)
	frappe.db.commit()

	print(
		f"Seeded {len(CATALOGUE)} accessories across {len(CATEGORIES)} categories "
		f"and {len(BRANDS)} brands."
	)
