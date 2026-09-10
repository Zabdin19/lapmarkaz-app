# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""TEST/VERIFICATION DATA for the Printing Machines + Printing Accessories
product line — NOT real inventory.

	bench --site site.localhost execute lapmarkaz_app.setup.printing_data.run

This seeds just enough taxonomy (a few machine/accessory types, three real
brand names) and a handful of clearly-fictional test products so every
filter, the compatibility system, cart and checkout can be exercised
end-to-end. Prices, specs and stock numbers below are illustrative only.

Before going live, replace the CATALOGUE/ACCESSORIES rows below with real
inventory from Desk (or delete these test records — they're re-identifiable
by name, e.g. "HP LaserJet Pro M404dn" — and re-run erpnext_setup.run to keep
the Item Groups). Re-runnable: existing records are updated in place.
"""

import frappe

IMG = "/assets/lapmarkaz_app/images/"
PRINTER_ART = IMG + "cat-printer.svg"
CARTRIDGE_ART = IMG + "cat-cartridge.svg"

MACHINE_TYPES = ["Laser Printer", "Inkjet Printer", "Multifunction Printer"]
BRANDS = ["HP", "Canon", "Epson"]
ACCESSORY_TYPES = ["Toner", "Ink Cartridge"]

# fmt: off
# name | brand | model | machine_type | tech | color | multifunction | print/scan/copy/fax | condition | price | wifi | duplex
MACHINES = [
	("HP LaserJet Pro M404dn", "HP", "M404dn", "Laser Printer", "Laser", "Monochrome",
	 0, (1, 0, 0, 0), "New", 45000, 0, 1),
	("HP LaserJet Pro MFP M428fdw", "HP", "MFP M428fdw", "Multifunction Printer", "Laser", "Monochrome",
	 1, (1, 1, 1, 1), "New", 78000, 1, 1),
	("Canon PIXMA G3010", "Canon", "PIXMA G3010", "Multifunction Printer", "Inkjet", "Color",
	 1, (1, 1, 1, 0), "New", 32000, 1, 0),
	("Epson EcoTank L3250", "Epson", "EcoTank L3250", "Multifunction Printer", "Inkjet", "Color",
	 1, (1, 1, 1, 0), "New", 38000, 1, 0),
	("Canon imageCLASS LBP6030", "Canon", "imageCLASS LBP6030", "Laser Printer", "Laser", "Monochrome",
	 0, (1, 0, 0, 0), "Refurbished", 22000, 0, 0),
]
# fmt: on

# accessory name | brand | model no. | type | price | compatible machine names
ACCESSORIES = [
	("HP 17A Black Toner Cartridge", "HP", "CF217A", "Toner", 8500,
	 ["HP LaserJet Pro M404dn", "HP LaserJet Pro MFP M428fdw"]),
	("HP 30A Black Toner Cartridge", "HP", "CF230A", "Toner", 7200,
	 ["HP LaserJet Pro M404dn"]),
	("Canon PG-47 Black Ink Cartridge", "Canon", "PG-47", "Ink Cartridge", 2800,
	 ["Canon PIXMA G3010"]),
	("Canon 325 Black Toner Cartridge", "Canon", "CRG-325", "Toner", 6500,
	 ["Canon imageCLASS LBP6030"]),
	("Epson 003 Black Ink Bottle", "Epson", "003", "Ink Cartridge", 1500,
	 ["Epson EcoTank L3250"]),
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
	for i, type_name in enumerate(MACHINE_TYPES):
		_ensure("Printing Machine Type", type_name, {"type_name": type_name, "display_order": i + 1})

	for i, brand in enumerate(BRANDS):
		_ensure("Printing Brand", brand, {"brand_name": brand, "display_order": i + 1})

	for i, type_name in enumerate(ACCESSORY_TYPES):
		_ensure("Printing Accessory Type", type_name, {"type_name": type_name, "display_order": i + 1})

	for name, brand, model, machine_type, tech, color, multi, caps, condition, price, wifi, duplex in MACHINES:
		can_print, can_scan, can_copy, can_fax = caps
		_ensure(
			"Printing Machine",
			name,
			{
				"machine_name": name,
				"slug": frappe.scrub(name).replace("_", "-"),
				"brand": brand,
				"model": model,
				"machine_type": machine_type,
				"print_technology": tech,
				"color_mode": color,
				"is_multifunction": multi,
				"can_print": can_print,
				"can_scan": can_scan,
				"can_copy": can_copy,
				"can_fax": can_fax,
				"condition": condition,
				"stock_status": "In Stock",
				"stock_qty": 10,
				"has_wifi": wifi,
				"has_duplex": duplex,
				"connectivity": "USB, Wi-Fi, Ethernet" if wifi else "USB, Ethernet",
				"price": price,
				"warranty": "1-Year Warranty" if condition == "New" else "6-Month Warranty",
				"thumbnail": PRINTER_ART,
				"tagline": f"{tech}, {color}" + (", Multifunction" if multi else ""),
				"description": (
					f"<p>The <b>{brand} {model}</b> is a {color.lower()} {tech.lower()} "
					f"{'multifunction ' if multi else ''}printer.</p>"
					"<p>[Test data — replace with real specifications before launch.]</p>"
				),
				"published": 1,
				"is_new_arrival": 1 if condition == "New" else 0,
				"is_featured": 1 if name in ("HP LaserJet Pro MFP M428fdw", "Canon PIXMA G3010") else 0,
			},
		)

	for name, brand, model, acc_type, price, compatible in ACCESSORIES:
		_ensure(
			"Printing Accessory",
			name,
			{
				"accessory_name": name,
				"slug": frappe.scrub(name).replace("_", "-"),
				"brand": brand,
				"accessory_type": acc_type,
				"tagline": f"Model {model}",
				"price": price,
				"image": CARTRIDGE_ART,
				"stock_status": "In Stock",
				"published": 1,
				"is_featured": 1 if acc_type == "Toner" else 0,
				"compatible_machines": [{"machine": m} for m in compatible],
				"description": (
					f"<p>Genuine-equivalent <b>{brand} {model}</b> {acc_type.lower()}.</p>"
					"<p>[Test data — replace with real specifications before launch.]</p>"
				),
			},
		)

	frappe.db.commit()

	print(
		f"[TEST DATA] Seeded {len(MACHINE_TYPES)} machine types, {len(BRANDS)} brands, "
		f"{len(ACCESSORY_TYPES)} accessory types, {len(MACHINES)} printing machines, "
		f"{len(ACCESSORIES)} printing accessories. Review and replace before going live."
	)
