# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Create the Lapmarkaz Desk workspace.

	bench --site site.localhost execute lapmarkaz_app.setup.workspace.run

Gives staff one place to reach the storefront masters instead of hunting
through the DocType list.
"""

import frappe

WORKSPACE = "Lapmarkaz"

SHORTCUTS = [
	("Laptop", "Laptop"),
	("Lapmarkaz Accessory", "Accessories"),
	("Sales Order", "Orders"),
	("Lapmarkaz Payment Method", "Payment Methods"),
	("Lapmarkaz Shop Settings", "Shop Settings"),
	("Home Page Settings", "Home Page"),
]

LINK_GROUPS = [
	("Catalogue", ["Laptop", "Laptop Brand", "Laptop Usage", "Laptop Review",
	               "Lapmarkaz Accessory", "Accessory Category", "Accessory Brand"]),
	("Sales", ["Sales Order", "Customer", "Lapmarkaz Cart", "Lapmarkaz Address",
	           "Lapmarkaz Payment Method", "Lapmarkaz Shop Settings"]),
	("Content", ["Home Page Settings", "About Page Settings", "Accessories Page Settings",
	             "Support Page Settings", "Store Locator Settings",
	             "Lapmarkaz Policy Page", "Lapmarkaz Store", "Lapmarkaz Hero Slide"]),
	("Customers", ["Lapmarkaz Support Message", "Lapmarkaz Wishlist Item"]),
]


def run():
	if frappe.db.exists("Workspace", WORKSPACE):
		frappe.delete_doc("Workspace", WORKSPACE, force=1, ignore_permissions=True)

	doc = frappe.get_doc(
		{
			"doctype": "Workspace",
			"name": WORKSPACE,
			"label": WORKSPACE,
			"title": WORKSPACE,
			"module": "Lapmarkaz",
			"icon": "retail",
			"public": 1,
			"is_hidden": 0,
			"sequence_id": 1.0,
		}
	)

	for doctype, label in SHORTCUTS:
		if frappe.db.exists("DocType", doctype):
			doc.append("shortcuts", {"type": "DocType", "link_to": doctype, "label": label})

	for group, doctypes in LINK_GROUPS:
		present = [d for d in doctypes if frappe.db.exists("DocType", d)]
		if not present:
			continue

		doc.append(
			"links",
			{
				"type": "Card Break",
				"label": group,
				"link_count": len(present),
				"onboard": 0,
			},
		)
		for doctype in present:
			doc.append(
				"links",
				{
					"type": "Link",
					"link_type": "DocType",
					"link_to": doctype,
					"label": doctype.replace("Lapmarkaz ", ""),
					"onboard": 0,
				},
			)

	doc.insert(ignore_permissions=True)
	frappe.db.commit()

	print(f"Workspace '{WORKSPACE}' created with {len(doc.shortcuts)} shortcuts "
	      f"and {len([l for l in doc.links if l.type == 'Link'])} links.")
