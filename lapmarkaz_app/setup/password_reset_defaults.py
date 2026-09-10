# Copyright (c) 2026, Lapmarkaz and contributors
# For license information, please see license.txt

"""Seed the branded password-reset email.

	bench --site site.localhost execute lapmarkaz_app.setup.password_reset_defaults.run

Frappe's `User.password_reset_mail()` reads `System Settings.reset_password_template`
and, when it points at an Email Template, renders that instead of its own plain
`templates/emails/password_reset.html`. So branding the email is a matter of
creating the record and pointing the setting at it — no core override.

The template is rendered with the context Frappe's `send_login_mail()` builds:
`first_name`, `user`, `title`, `login_url`, `created_by`, and `link` (the
/update-password URL carrying the reset key).

Re-runnable. The template body is rewritten on every run so edits here ship,
but the record is matched by name so Desk never accumulates duplicates.
"""

import frappe

TEMPLATE_NAME = "Lapmarkaz Password Reset"
SUBJECT = "Reset your hamzatraders password"

BRAND = "#0B5FD5"
NAVY = "#101B33"
INK = "#0F172A"
MUTED = "#64748B"
LINE = "#E5E9F0"
PAGE = "#F6F8FB"

# Table-based with inline styles: Outlook and Gmail strip <style> blocks and
# ignore flexbox, so this deliberately reads nothing like the storefront's CSS.
RESPONSE_HTML = f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
	style="background-color:{PAGE};margin:0;padding:32px 12px;">
	<tr>
		<td align="center">
			<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
				style="max-width:520px;background-color:#ffffff;border:1px solid {LINE};
				border-radius:14px;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,
				'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">

				<!-- masthead -->
				<tr>
					<td style="background-color:{NAVY};padding:24px 32px;">
						<span style="font-size:20px;font-weight:700;letter-spacing:-0.02em;color:#ffffff;">
							hamzatraders
						</span>
					</td>
				</tr>

				<!-- body -->
				<tr>
					<td style="padding:36px 32px 8px 32px;">
						<h1 style="margin:0 0 14px 0;font-size:23px;line-height:1.3;font-weight:700;
							letter-spacing:-0.02em;color:{INK};">
							Reset your password
						</h1>

						<p style="margin:0 0 16px 0;font-size:15px;line-height:1.6;color:{MUTED};">
							Hi {{{{ first_name }}}},
						</p>

						<p style="margin:0 0 26px 0;font-size:15px;line-height:1.6;color:{MUTED};">
							We received a request to reset the password for the hamzatraders account
							registered to <strong style="color:{INK};">{{{{ user }}}}</strong>.
							Click the button below to choose a new one.
						</p>

						<!-- CTA -->
						<table role="presentation" cellpadding="0" cellspacing="0" border="0"
							style="margin:0 0 26px 0;">
							<tr>
								<td align="center" bgcolor="{BRAND}" style="border-radius:9px;">
									<a href="{{{{ link }}}}"
										style="display:inline-block;padding:14px 34px;font-size:15px;
										font-weight:600;color:#ffffff;text-decoration:none;border-radius:9px;">
										Reset My Password
									</a>
								</td>
							</tr>
						</table>

						<p style="margin:0 0 8px 0;font-size:13px;line-height:1.6;color:{MUTED};">
							This link can only be used once, and expires shortly after it was sent.
							If it has already lapsed, request a new one from the
							<a href="{{{{ login_url }}}}/forgot-password" style="color:{BRAND};
								text-decoration:none;font-weight:600;">forgot password</a> page.
						</p>
					</td>
				</tr>

				<!-- fallback link -->
				<tr>
					<td style="padding:18px 32px 0 32px;">
						<p style="margin:0 0 6px 0;font-size:12px;color:{MUTED};">
							Button not working? Paste this into your browser:
						</p>
						<p style="margin:0;font-size:12px;line-height:1.5;word-break:break-all;">
							<a href="{{{{ link }}}}" style="color:{BRAND};text-decoration:none;">{{{{ link }}}}</a>
						</p>
					</td>
				</tr>

				<!-- footer -->
				<tr>
					<td style="padding:26px 32px 30px 32px;">
						<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
							<tr><td style="border-top:1px solid {LINE};height:1px;font-size:0;">&nbsp;</td></tr>
						</table>
						<p style="margin:20px 0 0 0;font-size:13px;line-height:1.6;color:{MUTED};">
							<strong style="color:{INK};">Didn't request this?</strong> You can safely ignore
							this email — your password will stay exactly as it is, and no one can change it
							without this link.
						</p>
						<p style="margin:18px 0 0 0;font-size:12px;line-height:1.7;color:#94A3B8;">
							hamzatraders &middot; Karachi, Pakistan<br>
							<a href="mailto:Info@lapmarkaz.pk" style="color:#94A3B8;text-decoration:none;">
								Info@lapmarkaz.pk</a> &middot; +92 321 2789920
						</p>
					</td>
				</tr>
			</table>
		</td>
	</tr>
</table>
""".strip()


def run():
	"""Create/refresh the template and point System Settings at it."""
	if frappe.db.exists("Email Template", TEMPLATE_NAME):
		template = frappe.get_doc("Email Template", TEMPLATE_NAME)
	else:
		template = frappe.new_doc("Email Template")
		template.name = TEMPLATE_NAME

	template.subject = SUBJECT
	template.use_html = 1
	template.response_html = RESPONSE_HTML
	# `response` is what Desk shows in the rich-text tab; keep it in step so the
	# record does not look empty when someone opens it.
	template.response = RESPONSE_HTML
	template.save(ignore_permissions=True)

	settings = frappe.get_single("System Settings")
	if settings.reset_password_template != TEMPLATE_NAME:
		settings.reset_password_template = TEMPLATE_NAME
		settings.flags.ignore_mandatory = True
		settings.save(ignore_permissions=True)

	frappe.db.commit()
	print(f"Email Template '{TEMPLATE_NAME}' seeded and wired to System Settings.")
