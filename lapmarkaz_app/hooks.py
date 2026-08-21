app_name = "lapmarkaz_app"
app_title = "lapmarkaz"
app_publisher = "zain ul abdin"
app_description = "Custom app for Lapmarkaz"
app_email = "zainulabdin1220@gmail.com"
app_license = "mit"

# Apps
# ------------------

# Website orders are Sales Orders, and the catalogue is provisioned into
# Items, so ERPNext is a hard dependency rather than an optional integration.
required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "lapmarkaz_app",
# 		"logo": "/assets/lapmarkaz_app/logo.png",
# 		"title": "lapmarkaz",
# 		"route": "/lapmarkaz_app",
# 		"has_permission": "lapmarkaz_app.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/lapmarkaz_app/css/lapmarkaz_app.css"
# app_include_js = "/assets/lapmarkaz_app/js/lapmarkaz_app.js"

# include js, css files in header of web template
# web_include_css = "/assets/lapmarkaz_app/css/lapmarkaz_app.css"
# web_include_js = "/assets/lapmarkaz_app/js/lapmarkaz_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "lapmarkaz_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "lapmarkaz_app/public/icons.svg"

# Home Pages
# ----------

home_page = "index"

# Exportable/versionable records: `bench --site <site> export-fixtures`
fixtures = [
	{"dt": "Lapmarkaz Payment Method"},
	{"dt": "Email Template", "filters": [["name", "in", ["Lapmarkaz Password Reset"]]]},
	{"dt": "Role", "filters": [["name", "in", ["Lapmarkaz Manager"]]]},
]

# Website
# -------

update_website_context = "lapmarkaz_app.website_context.update_context"

# Carry an anonymous cart into the account on login / signup.
on_session_creation = ["lapmarkaz_app.api.auth.after_login"]

# Frappe already refuses Website Users at /app with a PermissionError; this
# turns that dead end into a redirect back to the customer portal.
before_request = ["lapmarkaz_app.api.portal.block_website_users_from_desk"]

website_route_rules = [
	{"from_route": "/laptops/<slug>", "to_route": "laptop"},
	{"from_route": "/order/<order_id>", "to_route": "order-confirmation"},
	# ERPNext ships its own www/support page and, being installed after this
	# app, wins the name. Ours lives under a unique page name and claims the URL.
	{"from_route": "/support", "to_route": "help-center"},
	# ERPNext also claims /orders -> Sales Order and /addresses -> Address for
	# its generic portal. Web orders are Sales Orders now too, but they are
	# presented in the storefront's own design, so these rules point both routes
	# back at our pages rather than ERPNext's.
	{"from_route": "/orders", "to_route": "orders"},
	{"from_route": "/addresses", "to_route": "addresses"},
]

# Jinja helpers used across the storefront templates
jinja = {
	"methods": [
		"lapmarkaz_app.utils.jinja.rupees",
		"lapmarkaz_app.utils.jinja.condition_pill",
		"lapmarkaz_app.utils.jinja.condition_class",
		"lapmarkaz_app.utils.jinja.product_image",
	]
}

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "lapmarkaz_app.utils.jinja_methods",
# 	"filters": "lapmarkaz_app.utils.jinja_filters"
# }

# Installation
# ------------

# Provisions the Company, item groups and the `lm_*` Sales Order custom fields
# that checkout writes to. Idempotent, and re-run after every migrate so a
# field added in a later release lands without a manual step.
after_install = "lapmarkaz_app.setup.erpnext_setup.run"
after_migrate = "lapmarkaz_app.setup.erpnext_setup.after_migrate"

# before_install = "lapmarkaz_app.install.before_install"

# Uninstallation
# ------------

# before_uninstall = "lapmarkaz_app.uninstall.before_uninstall"
# after_uninstall = "lapmarkaz_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "lapmarkaz_app.utils.before_app_install"
# after_app_install = "lapmarkaz_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "lapmarkaz_app.utils.before_app_uninstall"
# after_app_uninstall = "lapmarkaz_app.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "lapmarkaz_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------

# Keep the ERPNext Item behind a catalogue record in step with it. Products
# that have never been ordered have no Item yet and are skipped.
doc_events = {
	"Laptop": {"on_update": "lapmarkaz_app.utils.items.sync_item"},
	"Lapmarkaz Accessory": {"on_update": "lapmarkaz_app.utils.items.sync_item"},
	# Move the shopper's tracking timeline when staff submit or cancel, so the
	# customer-facing status can't silently fall behind the real one.
	"Sales Order": {
		"on_submit": "lapmarkaz_app.utils.sales_order.on_submit",
		"on_cancel": "lapmarkaz_app.utils.sales_order.on_cancel",
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"lapmarkaz_app.tasks.all"
# 	],
# 	"daily": [
# 		"lapmarkaz_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"lapmarkaz_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"lapmarkaz_app.tasks.weekly"
# 	],
# 	"monthly": [
# 		"lapmarkaz_app.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "lapmarkaz_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "lapmarkaz_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "lapmarkaz_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["lapmarkaz_app.utils.before_request"]
# after_request = ["lapmarkaz_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["lapmarkaz_app.utils.before_job"]
# after_job = ["lapmarkaz_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"lapmarkaz_app.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

