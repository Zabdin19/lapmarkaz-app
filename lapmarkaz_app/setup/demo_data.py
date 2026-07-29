# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Seed the laptop catalogue and hero slides.

Accessories are seeded separately by setup/accessories_data.py.

	bench --site site.localhost execute lapmarkaz_app.setup.demo_data.run

Re-runnable: existing records are updated in place, nothing is duplicated.
"""

import frappe

IMG = "/assets/lapmarkaz_app/images/"
SILVER, BLACK, GRAY = IMG + "laptop-silver.svg", IMG + "laptop-black.svg", IMG + "laptop-gray.svg"

BRANDS = ["HP", "Dell", "Lenovo", "Apple", "Asus", "Acer", "MSI", "Microsoft"]
USAGES = ["Student", "Business", "Gaming", "Programming", "Design", "Everyday"]

# fmt: off
# name | brand | model | cond | grade | cpu family | gen | cpu | ram | storage | screen | price | img | flags | usage
CATALOGUE = [
	("HP EliteBook 840 G5 16GB 256GB", "HP", "EliteBook 840 G5", "Grade A Refurbished", "A", "Core i5", "8th Gen", "Intel Core i5-8250U", 16, "256GB SSD", 14.0, 48000, SILVER, "featured", ["Business", "Student"]),
	("Lenovo ThinkPad T480 8GB 256GB", "Lenovo", "ThinkPad T480", "Certified Refurbished", "A", "Core i5", "8th Gen", "Intel Core i5-8250U", 8, "256GB SSD", 14.0, 45000, BLACK, "featured", ["Business", "Everyday"]),
	("Dell Latitude 7490 16GB 512GB", "Dell", "Latitude 7490", "Grade A Refurbished", "A", "Core i7", "8th Gen", "Intel Core i7-8650U", 16, "512GB SSD", 14.0, 55000, GRAY, "featured", ["Business", "Programming"]),
	("HP EliteBook 840 G5 16GB 512GB", "HP", "EliteBook 840 G5", "Grade A Refurbished", "A", "Core i5", "8th Gen", "Intel Core i5-8350U", 16, "512GB SSD", 14.0, 65000, SILVER, "new", ["Business", "Programming"]),
	("Dell Latitude 5490 8GB 256GB", "Dell", "Latitude 5490", "Grade A Refurbished", "A", "Core i5", "8th Gen", "Intel Core i5-8350U", 8, "256GB SSD", 14.0, 58000, GRAY, "new", ["Student", "Everyday"]),
	("Apple MacBook Air M1 2020", "Apple", "MacBook Air M1 (2020)", "New", "", "Apple M1", "M Series", "Apple M1 8-Core", 8, "256GB SSD", 13.3, 195000, GRAY, "new", ["Design", "Student"]),
	("Lenovo ThinkPad T480 16GB 512GB", "Lenovo", "ThinkPad T480", "Certified Refurbished", "A", "Core i5", "8th Gen", "Intel Core i5-8350U", 16, "512GB SSD", 14.0, 62000, BLACK, "new,featured,best", ["Business", "Programming"]),
	("Lenovo ThinkPad T470s 8GB 256GB", "Lenovo", "ThinkPad T470s", "Grade B Refurbished", "B", "Core i5", "7th Gen", "Intel Core i5-7300U", 8, "256GB SSD", 14.0, 48000, BLACK, "", ["Everyday", "Student"]),
	("Apple MacBook Pro 13 2017", "Apple", 'MacBook Pro 13" (2017)', "Grade A Refurbished", "A", "Core i5", "7th Gen", "Intel Core i5-7360U", 8, "256GB SSD", 13.3, 95000, GRAY, "", ["Design", "Programming"]),
	("Lenovo ThinkPad X1 Carbon Gen 10", "Lenovo", "ThinkPad X1 Carbon Gen 10", "New", "", "Core i7", "12th Gen", "Intel Core i7-1260P", 16, "1TB SSD", 14.0, 350000, BLACK, "featured,best", ["Business", "Programming"]),
	("HP ProBook 450 G7 8GB 512GB", "HP", "ProBook 450 G7", "Grade A Refurbished", "A", "Core i5", "10th Gen", "Intel Core i5-10210U", 8, "512GB SSD", 15.6, 72000, SILVER, "", ["Student", "Everyday"]),
	("Dell XPS 13 9370 16GB 512GB", "Dell", "XPS 13 9370", "Grade A Refurbished", "A", "Core i7", "8th Gen", "Intel Core i7-8550U", 16, "512GB SSD", 13.3, 118000, GRAY, "best", ["Design", "Business"]),
	("Asus ROG Strix G15 16GB 1TB", "Asus", "ROG Strix G15", "New", "", "Ryzen 7", "11th Gen", "AMD Ryzen 7 6800H", 16, "1TB SSD", 15.6, 285000, BLACK, "featured", ["Gaming", "Design"]),
	("Acer Aspire 5 A515 8GB 512GB", "Acer", "Aspire 5 A515", "New", "", "Core i3", "11th Gen", "Intel Core i3-1115G4", 8, "512GB SSD", 15.6, 78000, SILVER, "", ["Student", "Everyday"]),
	("MSI GF63 Thin 16GB 512GB", "MSI", "GF63 Thin", "New", "", "Core i5", "11th Gen", "Intel Core i5-11400H", 16, "512GB SSD", 15.6, 210000, BLACK, "", ["Gaming"]),
	("Microsoft Surface Laptop 3 8GB 256GB", "Microsoft", "Surface Laptop 3", "Grade A Refurbished", "A", "Core i5", "10th Gen", "Intel Core i5-1035G7", 8, "256GB SSD", 13.5, 105000, GRAY, "", ["Design", "Student"]),
	("HP EliteBook 830 G6 16GB 512GB", "HP", "EliteBook 830 G6", "Grade A Refurbished", "A", "Core i5", "8th Gen", "Intel Core i5-8365U", 16, "512GB SSD", 13.3, 68000, SILVER, "", ["Business"]),
	("Dell Latitude 5400 8GB 256GB", "Dell", "Latitude 5400", "Grade B Refurbished", "B", "Core i5", "8th Gen", "Intel Core i5-8365U", 8, "256GB SSD", 14.0, 52000, GRAY, "", ["Everyday", "Business"]),
	("Lenovo IdeaPad Slim 3 8GB 512GB", "Lenovo", "IdeaPad Slim 3", "New", "", "Ryzen 5", "11th Gen", "AMD Ryzen 5 5500U", 8, "512GB SSD", 15.6, 84000, SILVER, "", ["Student", "Everyday"]),
	("Apple MacBook Air M2 2022", "Apple", "MacBook Air M2 (2022)", "New", "", "Apple M2", "M Series", "Apple M2 8-Core", 16, "512GB SSD", 13.6, 315000, GRAY, "best", ["Design", "Programming"]),
	("Asus VivoBook 15 8GB 512GB", "Asus", "VivoBook 15", "New", "", "Core i3", "10th Gen", "Intel Core i3-1005G1", 8, "512GB SSD", 15.6, 66000, SILVER, "", ["Student"]),
	("HP ZBook 15u G5 32GB 1TB", "HP", "ZBook 15u G5", "Grade A Refurbished", "A", "Core i7", "8th Gen", "Intel Core i7-8650U", 32, "1TB SSD", 15.6, 132000, SILVER, "", ["Design", "Programming"]),
	("Dell Precision 5530 32GB 1TB", "Dell", "Precision 5530", "Grade A Refurbished", "A", "Core i7", "8th Gen", "Intel Core i7-8850H", 32, "1TB SSD", 15.6, 165000, GRAY, "", ["Design", "Gaming"]),
	("Lenovo ThinkPad L390 4GB 128GB", "Lenovo", "ThinkPad L390", "Grade B Refurbished", "B", "Core i3", "8th Gen", "Intel Core i3-8145U", 4, "128GB SSD", 13.3, 34000, BLACK, "", ["Everyday", "Student"]),
]
# fmt: on

CPU_NOTES = {
	"Intel Core i5-8350U": "1.7 GHz Base, Up to 3.6 GHz, 4 Cores",
	"Intel Core i5-8250U": "1.6 GHz Base, Up to 3.4 GHz, 4 Cores",
	"Intel Core i7-8650U": "1.9 GHz Base, Up to 4.2 GHz, 4 Cores",
	"Intel Core i7-8550U": "1.8 GHz Base, Up to 4.0 GHz, 4 Cores",
}

GPUS = {
	"Core i3": ("Intel UHD Graphics 620", "Integrated, Shared Memory"),
	"Core i5": ("Intel UHD Graphics 620", "Integrated, Shared Memory"),
	"Core i7": ("Intel UHD Graphics 620", "Integrated, Shared Memory"),
	"Ryzen 5": ("AMD Radeon Graphics", "Integrated, Shared Memory"),
	"Ryzen 7": ("NVIDIA GeForce RTX 3060", "6GB GDDR6 Dedicated"),
	"Apple M1": ("Apple 7-Core GPU", "Unified Memory Architecture"),
	"Apple M2": ("Apple 10-Core GPU", "Unified Memory Architecture"),
}

HERO_SLIDES = [
	{
		"eyebrow": "STUDENT ESSENTIALS",
		"heading": "Student Laptops:\nBest price-to-performance",
		"subheading": "Equip yourself for success with lightweight, reliable machines designed for all-day campus life.",
		"cta_label": "Shop Now",
		"cta_link": "/shop?usage=Student",
		"image": IMG + "hero-student.svg",
		"display_order": 1,
	},
	{
		"eyebrow": "BUSINESS CLASS",
		"heading": "Certified Refurbished:\nEnterprise grade, honest prices",
		"subheading": "ThinkPads, EliteBooks and Latitudes tested across 40 checkpoints and backed by warranty.",
		"cta_label": "Shop Now",
		"cta_link": "/shop?usage=Business",
		"image": IMG + "hero-business.svg",
		"display_order": 2,
	},
	{
		"eyebrow": "PLAY HARDER",
		"heading": "Gaming Laptops:\nFrames that keep up with you",
		"subheading": "Dedicated graphics, high refresh panels and cooling built for long sessions.",
		"cta_label": "Shop Now",
		"cta_link": "/shop?usage=Gaming",
		"image": IMG + "hero-gaming.svg",
		"display_order": 3,
	},
]

REVIEWS = [
	("Ahmed Raza", 5, "Exactly as described", "Battery health was 92%, body is spotless. Shipped to Lahore in two days."),
	("Sana Iqbal", 5, "Great value", "Runs Android Studio and Chrome without a stutter. Very happy with the 16GB config."),
	("Bilal Hussain", 5, "Solid build", "The classic ThinkPad keyboard is still the best. Screen is bright and clear."),
	("Hira Malik", 4, "Good, minor scuff", "One small scratch on the lid, otherwise flawless. Grade A is accurate."),
	("Usman Tariq", 5, "Verified seller", "Got the invoice and warranty card. Verification call before shipping was reassuring."),
	("Ayesha Noor", 5, "Perfect for uni", "Light enough to carry all day and the dual battery genuinely lasts."),
	("Fahad Sheikh", 5, "Fast delivery", "Ordered Monday, arrived Wednesday in Karachi. Packaging was excellent."),
	("Nida Aslam", 4, "Happy overall", "Wish it came with a bigger charger, but performance is exactly what I needed."),
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
	for i, brand in enumerate(BRANDS):
		_ensure("Laptop Brand", brand, {"brand_name": brand, "display_order": i + 1})

	for usage in USAGES:
		_ensure("Laptop Usage", usage, {"usage_name": usage})

	for row in CATALOGUE:
		(
			name, brand, model, condition, grade, family, gen, cpu,
			ram, storage, screen, price, image, flags, usages,
		) = row

		flags = flags.split(",") if flags else []
		gpu, gpu_note = GPUS.get(family, ("Integrated Graphics", "Shared Memory"))
		storage_gb = 1024 if storage.startswith("1TB") else int(storage.split("GB")[0])
		tagline = f"{family} {gen}, {ram}GB RAM, {storage}" if gen != "M Series" else f"{ram}GB Unified Memory, {storage}"

		_ensure(
			"Laptop",
			name,
			{
				"laptop_name": name,
				"brand": brand,
				"model": model,
				"slug": frappe.scrub(name).replace("_", "-"),
				"tagline": tagline,
				"condition": condition,
				"grade": grade,
				"stock_status": "In Stock",
				"stock_qty": 6,
				"processor": cpu,
				"processor_family": family,
				"generation": gen,
				"processor_note": CPU_NOTES.get(cpu, "Turbo Boost, Multi-Core"),
				"ram_gb": ram,
				"ram_spec": f"{ram}GB DDR4" if not family.startswith("Apple") else f"{ram}GB Unified",
				"ram_note": "2400 MHz (Upgradable to 32GB)" if not family.startswith("Apple") else "On-package memory",
				"storage": storage.replace("GB SSD", "GB NVMe SSD").replace("1TB SSD", "1TB NVMe SSD"),
				"storage_gb": storage_gb,
				"storage_note": "PCIe Fast Storage",
				"screen_size": screen,
				"display": f'{screen:g}" FHD IPS Anti-Glare' if screen != 13.3 else f'{screen:g}" Retina Display',
				"display_note": "1920 x 1080 Resolution" if screen != 13.3 else "2560 x 1600 Resolution",
				"gpu": gpu,
				"gpu_note": gpu_note,
				"battery": "Dual Battery System" if "ThinkPad" in model else "Long Life Battery",
				"battery_note": "Power Bridge Technology" if "ThinkPad" in model else "Up to 10 Hours Usage",
				"ports": "USB-C, HDMI, RJ45" if "ThinkPad" in model or "EliteBook" in model else "USB-C, USB-A, HDMI",
				"ports_note": "Thunderbolt 3, Wi-Fi 5, Bluetooth 4.1",
				"price": price,
				"price_note": "Price includes taxes. Free shipping on this item.",
				"shipping_note": "Free Nationwide Shipping",
				"return_note": "7-Day Easy Return",
				"warranty": "1-Month Warranty" if condition != "New" else "1-Year Warranty",
				"thumbnail": image,
				"images": [
					{"image": image, "alt_text": f"{brand} {model} front"},
					{"image": image, "alt_text": f"{brand} {model} keyboard"},
					{"image": image, "alt_text": f"{brand} {model} side"},
				],
				"description": _description(brand, model, condition, cpu, ram, storage),
				"published": 1,
				"is_new_arrival": 1 if "new" in flags else 0,
				"is_featured": 1 if "featured" in flags else 0,
				"is_best_seller": 1 if "best" in flags else 0,
				"usage_tags": [{"usage": u} for u in usages],
			},
		)

	frappe.db.delete("Lapmarkaz Hero Slide")
	for slide in HERO_SLIDES:
		frappe.get_doc({"doctype": "Lapmarkaz Hero Slide", "published": 1, **slide}).insert(
			ignore_permissions=True
		)

	_seed_reviews("Lenovo ThinkPad T480 16GB 512GB", 24)
	_seed_reviews("HP EliteBook 840 G5 16GB 512GB", 11)
	_seed_reviews("Dell Latitude 7490 16GB 512GB", 8)
	_seed_reviews("Apple MacBook Air M1 2020", 17)

	frappe.db.commit()
	print(f"Seeded {len(CATALOGUE)} laptops and {len(HERO_SLIDES)} hero slides.")


def _description(brand, model, condition, cpu, ram, storage):
	return (
		f"<p>The <b>{brand} {model}</b> pairs a {cpu} with {ram}GB of memory and a {storage}, "
		"making it a dependable everyday machine for work, study and everything in between.</p>"
		f"<p>This unit is supplied as <b>{condition}</b>. Every Lapmarkaz laptop is inspected across a "
		"40-point checklist covering battery health, keyboard, hinges, ports, display uniformity and "
		"thermals before it is listed.</p>"
		"<ul><li>Genuine Windows / macOS installation</li>"
		"<li>Battery health verified above 80%</li>"
		"<li>Original charger included</li>"
		"<li>Backed by our warranty and 7-day easy return</li></ul>"
	)


def _seed_reviews(laptop, target):
	if not frappe.db.exists("Laptop", laptop):
		return

	frappe.db.delete("Laptop Review", {"laptop": laptop})
	for i in range(target):
		reviewer, rating, title, comment = REVIEWS[i % len(REVIEWS)]
		suffix = "" if i < len(REVIEWS) else f" {i // len(REVIEWS) + 1}"
		frappe.get_doc(
			{
				"doctype": "Laptop Review",
				"laptop": laptop,
				"reviewer_name": reviewer + suffix,
				"rating": rating,
				"title": title,
				"comment": comment,
				"verified_purchase": 1,
			}
		).insert(ignore_permissions=True)
