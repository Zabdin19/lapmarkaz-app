# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Explicitly replace legacy public branding stored in site data.

Run deliberately after deploying the rebrand:

	bench --site <site> execute lapmarkaz_app.setup.branding.run

This is intentionally not a migration hook. It changes only known legacy
values, so customized titles and copy are left untouched.
"""

import frappe


SINGLE_REPLACEMENTS = {
	"Home Page Settings": {
		"page_title": {
			"Lapmarkaz — Premium Tech for Pakistan": "HamzaTraders — Premium Tech for Pakistan",
			"hamzatraders — Premium Tech for Pakistan": "HamzaTraders — Premium Tech for Pakistan",
		},
		"why_choose_heading": {
			"Why Choose Lapmarkaz": "Why Choose HamzaTraders",
			"Why Choose hamzatraders": "Why Choose HamzaTraders",
		},
		"footer_note": {
			"© 2024 Lapmarkaz Pakistan. All rights reserved.": (
				"© 2024 HamzaTraders Pakistan. All rights reserved."
			),
			"© 2024 hamzatraders Pakistan. All rights reserved.": (
				"© 2024 HamzaTraders Pakistan. All rights reserved."
			),
		},
	},
	"Accessories Page Settings": {
		"page_title": {
			"Premium Accessories | Lapmarkaz": "Premium Accessories | HamzaTraders",
			"Premium Accessories | hamzatraders": "Premium Accessories | HamzaTraders",
		},
		"footer_note": {
			"© 2024 Lapmarkaz. All rights reserved. High-performance computing for Pakistan.": (
				"© 2024 HamzaTraders. All rights reserved. High-performance computing for Pakistan."
			),
			"© 2024 hamzatraders. All rights reserved. High-performance computing for Pakistan.": (
				"© 2024 HamzaTraders. All rights reserved. High-performance computing for Pakistan."
			),
		},
	},
	"About Page Settings": {
		"page_title": {
			"About Us | Lapmarkaz": "About Us | HamzaTraders",
			"About Us | hamzatraders": "About Us | HamzaTraders",
		},
		"footer_note": {
			"© 2024 Lapmarkaz Pakistan. All rights reserved.": (
				"© 2024 HamzaTraders Pakistan. All rights reserved."
			),
			"© 2024 hamzatraders Pakistan. All rights reserved.": (
				"© 2024 HamzaTraders Pakistan. All rights reserved."
			),
		},
	},
	"Store Locator Settings": {
		"page_title": {
			"Store Locator | Lapmarkaz": "Store Locator | HamzaTraders",
			"Store Locator | hamzatraders": "Store Locator | HamzaTraders",
		},
		"heading": {
			"Find a Lapmarkaz Store": "Find a HamzaTraders Store",
			"Find a hamzatraders Store": "Find a HamzaTraders Store",
		},
	},
	"Support Page Settings": {
		"page_title": {
			"Support | Lapmarkaz": "Support | HamzaTraders",
			"Support | hamzatraders": "Support | HamzaTraders",
		},
		"footer_note": {
			"© 2024 Lapmarkaz. All rights reserved.": "© 2024 HamzaTraders. All rights reserved.",
			"© 2024 hamzatraders. All rights reserved.": "© 2024 HamzaTraders. All rights reserved.",
		},
	},
}


def _canonical_title(value):
	if not value:
		return value

	if value in {
		"Lapmarkaz — Premium Tech for Pakistan",
		"hamzatraders — Premium Tech for Pakistan",
	}:
		return "HamzaTraders — Premium Tech for Pakistan"

	for suffix in (" | Lapmarkaz", " | hamzatraders"):
		if value.endswith(suffix):
			return f"{value[:-len(suffix)]} | HamzaTraders"

	return value


def _update_single(doctype, replacements):
	doc = frappe.get_single(doctype)
	changed = []

	for fieldname, values in replacements.items():
		current = doc.get(fieldname)
		if current in values:
			doc.set(fieldname, values[current])
			changed.append(fieldname)

	if changed:
		doc.save(ignore_permissions=True)

	return changed


def _update_policy_titles():
	changed = []
	for name in frappe.get_all("Lapmarkaz Policy Page", pluck="name"):
		doc = frappe.get_doc("Lapmarkaz Policy Page", name)
		canonical = _canonical_title(doc.meta_title)
		if canonical != doc.meta_title:
			doc.meta_title = canonical
			doc.save(ignore_permissions=True)
			changed.append(name)
	return changed


def _update_route_meta_titles():
	changed = []
	for route in frappe.get_all("Website Route Meta", pluck="name"):
		doc = frappe.get_doc("Website Route Meta", route)
		dirty = False
		for row in doc.meta_tags:
			if row.key not in {"title", "og:title", "twitter:title"}:
				continue
			canonical = _canonical_title(row.value)
			if canonical != row.value:
				row.value = canonical
				dirty = True
		if dirty:
			doc.save(ignore_permissions=True)
			changed.append(route)
	return changed


def run():
	"""Update exact legacy branding values and return a change summary."""
	changed = {
		doctype: _update_single(doctype, replacements)
		for doctype, replacements in SINGLE_REPLACEMENTS.items()
	}
	changed["Lapmarkaz Policy Page"] = _update_policy_titles()
	changed["Website Route Meta"] = _update_route_meta_titles()
	frappe.db.commit()
	return {doctype: fields for doctype, fields in changed.items() if fields}
