/* Lapmarkaz storefront behaviour: cart badge, add-to-cart, hero carousel. */
(function () {
	"use strict";

	const API = "/api/method/lapmarkaz_app.api.cart.";

	function call(method, args) {
		return fetch(API + method, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-Frappe-CSRF-Token": (window.frappe && frappe.csrf_token) || "",
			},
			credentials: "same-origin",
			body: JSON.stringify(args || {}),
		})
			.then((r) => r.json())
			.then((r) => r.message);
	}

	const money = (n) =>
		"Rs. " + Number(n || 0).toLocaleString("en-PK", { maximumFractionDigits: 0 });

	// ---------------------------------------------------------------- badge

	function paintBadge(count) {
		document.querySelectorAll("[data-lm-cart-badge]").forEach((el) => {
			el.textContent = count;
			el.classList.toggle("hidden", !count);
		});
	}

	function refreshBadge() {
		return call("count").then((r) => {
			paintBadge((r && r.count) || 0);
			return r;
		});
	}

	// ------------------------------------------------------------ add to cart

	function flash(button, label) {
		const original = button.getAttribute("data-lm-label") || button.innerHTML;
		button.setAttribute("data-lm-label", original);
		button.disabled = true;
		if (button.dataset.lmText === "1") button.textContent = label;
		setTimeout(() => {
			button.disabled = false;
			if (button.dataset.lmText === "1") button.innerHTML = original;
		}, 1100);
	}

	function toast(message) {
		let host = document.getElementById("lm-toast");
		if (!host) {
			host = document.createElement("div");
			host.id = "lm-toast";
			host.className = "fixed bottom-6 left-1/2 z-50 -translate-x-1/2 space-y-2";
			document.body.appendChild(host);
		}
		const el = document.createElement("div");
		el.className =
			"rounded-lg bg-ink px-4 py-2.5 text-sm font-medium text-white shadow-pop transition " +
			"opacity-0 translate-y-2";
		el.textContent = message;
		host.appendChild(el);
		requestAnimationFrame(() => el.classList.remove("opacity-0", "translate-y-2"));
		setTimeout(() => {
			el.classList.add("opacity-0", "translate-y-2");
			setTimeout(() => el.remove(), 250);
		}, 2200);
	}

	document.addEventListener("click", function (event) {
		const button = event.target.closest("[data-lm-add]");
		if (!button) return;

		event.preventDefault();
		const qtyInput = button.dataset.lmQtyFrom
			? document.querySelector(button.dataset.lmQtyFrom)
			: null;

		flash(button, "Added");
		call("add", {
			item: button.dataset.lmAdd,
			item_type: button.dataset.lmType || "Laptop",
			qty: qtyInput ? qtyInput.value : button.dataset.lmQty || 1,
		}).then((cart) => {
			paintBadge((cart && cart.total_qty) || 0);
			if (button.dataset.lmThen === "cart") {
				window.location.href = "/cart";
			} else if (button.dataset.lmThen === "checkout") {
				window.location.href = "/checkout";
			} else {
				toast("Added to cart");
			}
		});
	});

	// ------------------------------------------------------------- wishlist

	function currentUserIsGuest() {
		// frappe.boot.user is a desk-only field and is undefined on website
		// pages, so it can't tell guest and signed-in visitors apart here.
		// Frappe's base.html always stamps the real session state onto
		// <body frappe-session-status="logged-in|logged-out">; read that instead.
		return document.body.getAttribute("frappe-session-status") !== "logged-in";
	}

	function paintWishlistButton(button, saved) {
		button.classList.toggle("text-brand", saved);
		button.classList.toggle("text-slate-400", !saved);
		button.setAttribute("aria-label", saved ? "Remove from wishlist" : "Add to wishlist");

		const path = button.querySelector("svg path");
		if (path) {
			path.setAttribute("fill", saved ? "currentColor" : "none");
			path.setAttribute("stroke", saved ? "none" : "currentColor");
		}
	}

	document.addEventListener("click", function (event) {
		const button = event.target.closest("[data-lm-wishlist]");
		if (!button) return;

		event.preventDefault();

		if (currentUserIsGuest()) {
			const back = window.location.pathname + window.location.search;
			window.location.href = "/login?redirect-to=" + encodeURIComponent(back);
			return;
		}

		const laptop = button.dataset.lmWishlist;
		button.disabled = true;

		fetch("/api/method/lapmarkaz_app.api.wishlist.toggle", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-Frappe-CSRF-Token": (window.frappe && frappe.csrf_token) || "",
			},
			credentials: "same-origin",
			body: JSON.stringify({ laptop: laptop }),
		})
			.then((r) => r.json())
			.then((r) => {
				const saved = !!(r.message && r.message.saved);
				document
					.querySelectorAll('[data-lm-wishlist="' + laptop.replace(/"/g, "") + '"]')
					.forEach((btn) => paintWishlistButton(btn, saved));
				toast(saved ? "Added to wishlist" : "Removed from wishlist");
			})
			.finally(() => {
				button.disabled = false;
			});
	});

	// --------------------------------------------------------------- logout

	// Frappe's /api/method/logout deletes ONLY the current session's sid and
	// clears this browser's cookie. It deliberately does not call
	// clear_sessions(), so a Desk session for another user in another browser
	// is untouched.
	document.addEventListener("click", function (event) {
		const button = event.target.closest("[data-lm-logout]");
		if (!button) return;

		event.preventDefault();
		button.disabled = true;

		fetch("/api/method/logout", {
			method: "POST",
			headers: { "X-Frappe-CSRF-Token": (window.frappe && frappe.csrf_token) || "" },
			credentials: "same-origin",
		}).then(function () {
			window.location.href = "/";
		});
	});

	// ------------------------------------------------------------- carousel

	function initCarousel(root) {
		const slides = Array.from(root.querySelectorAll("[data-lm-slide]"));
		const dots = Array.from(root.querySelectorAll("[data-lm-dot]"));
		if (slides.length < 2) return;

		let index = 0;
		let timer;

		function show(next) {
			index = (next + slides.length) % slides.length;
			slides.forEach((s, i) => {
				s.classList.toggle("opacity-0", i !== index);
				s.classList.toggle("pointer-events-none", i !== index);
			});
			dots.forEach((d, i) => {
				d.classList.toggle("w-7", i === index);
				d.classList.toggle("bg-brand", i === index);
				d.classList.toggle("w-2.5", i !== index);
				d.classList.toggle("bg-white/45", i !== index);
			});
		}

		function play() {
			clearInterval(timer);
			timer = setInterval(() => show(index + 1), 6000);
		}

		dots.forEach((dot, i) =>
			dot.addEventListener("click", () => {
				show(i);
				play();
			})
		);

		show(0);
		play();
	}

	// ---------------------------------------------------------- scroll reveal

	function initReveal() {
		var sections = document.querySelectorAll("[data-lm-reveal]");
		if (!sections.length) return;

		var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
		if (reduceMotion || !("IntersectionObserver" in window)) {
			sections.forEach((el) => el.classList.add("lm-revealed"));
			return;
		}

		var observer = new IntersectionObserver(
			function (entries) {
				entries.forEach(function (entry) {
					if (entry.isIntersecting) {
						entry.target.classList.add("lm-revealed");
						observer.unobserve(entry.target);
					}
				});
			},
			{ rootMargin: "0px 0px -10% 0px", threshold: 0.1 }
		);

		sections.forEach((el) => observer.observe(el));
	}

	// -------------------------------------------------------------- faq accordion

	document.addEventListener("click", function (event) {
		const button = event.target.closest("[data-lm-faq-toggle]");
		if (!button) return;

		const panel = document.getElementById(button.getAttribute("aria-controls"));
		if (!panel) return;

		const open = button.getAttribute("aria-expanded") === "true";
		button.setAttribute("aria-expanded", String(!open));
		panel.classList.toggle("is-open", !open);
	});

	// ---------------------------------------------------------------- boot

	// After a guest cart is merged on login, tell the customer if anything was
	// dropped (out of stock / unpublished) or capped at available stock.
	function showMergeNotice() {
		if (document.body.getAttribute("frappe-session-status") !== "logged-in") return;

		fetch("/api/method/lapmarkaz_app.api.cart.merge_notice", { credentials: "same-origin" })
			.then((r) => r.json())
			.then((r) => {
				const notice = r.message || {};
				if (notice.removed && notice.removed.length) {
					toast("Removed from your cart (unavailable): " + notice.removed.join(", "));
				}
				if (notice.capped && notice.capped.length) {
					toast("Reduced to available stock: " + notice.capped.join(", "));
				}
			})
			.catch(() => {});
	}

	document.addEventListener("DOMContentLoaded", function () {
		document.querySelectorAll("[data-lm-carousel]").forEach(initCarousel);
		initReveal();
		refreshBadge();
		showMergeNotice();
	});

	window.lapmarkaz = { call, refreshBadge, paintBadge, money, toast };
})();
