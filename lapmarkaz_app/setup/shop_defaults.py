# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Seed Lapmarkaz Shop Settings.

	bench --site site.localhost execute lapmarkaz_app.setup.shop_defaults.run

A Single's field defaults only exist once the record has been saved, so this
must run before checkout reads the shipping numbers.
"""

import frappe


def run():
	settings = frappe.get_single("Lapmarkaz Shop Settings")
	settings.update(
		{
			"require_login_to_order": 0,
			"login_required_message": "Please sign in to place your order.",
			"allow_guest_cart": 1,
			"free_shipping_over": 20000,
			"shipping_charge": 500,
			"delivery_days": 4,
			"reduce_stock_on_order": 1,
		}
	)
	settings.save(ignore_permissions=True)
	frappe.db.commit()

	print(
		"Shop settings seeded — require_login_to_order:",
		settings.require_login_to_order,
		"| free shipping over:",
		settings.free_shipping_over,
	)
