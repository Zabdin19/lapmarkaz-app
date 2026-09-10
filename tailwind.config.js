/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./lapmarkaz_app/**/*.html",
    "./lapmarkaz_app/**/*.py",
    "./lapmarkaz_app/**/*.js",
  ],
  theme: {
    extend: {
      colors: (() => {
        // Success/warning/danger are semantic aliases of mint/amber/red so the
        // hex values live in exactly one place instead of being duplicated.
        const mint = {
          50: "#EAFBF4",
          100: "#CFF5E4",
          400: "#35D6A4", // original bright mint — decorative/large-surface use only
          500: "#22C08C",
          DEFAULT: "#0D8058", // AA-safe on white (4.95:1) — badges/buttons/text
          600: "#0D8058",
          700: "#0A6B49",
        };
        const amber = {
          50: "#FFF7ED",
          100: "#FEF3C7",
          400: "#FBBF24", // rating stars — decorative only
          DEFAULT: "#B45309", // AA-safe on white (5.02:1)
          600: "#B45309",
          700: "#92400E",
        };
        const red = {
          50: "#FEF2F2",
          100: "#FEE2E2",
          400: "#F87171", // soft validation-border tint, decorative only
          DEFAULT: "#DC2626", // AA-safe on white (4.83:1)
          600: "#DC2626",
          700: "#B91C1C",
        };

        return {
          brand: {
            50: "#EEF4FF",
            100: "#DCE9FC",
            500: "#2E8BFF", // literal logo blue (logo-mark.svg) — icons/gradients only, not text/white-on-color
            DEFAULT: "#0E56D9", // refined primary — 6.27:1 white text (was 5.81:1)
            600: "#0E56D9",
            700: "#0A44B0", // hover — 8.51:1
            800: "#083588", // active
          },
          ink: "#0F172A",
          navy: {
            DEFAULT: "#101B33",
            700: "#1E2C4A",
            800: "#16233F",
            900: "#0B1526",
          },
          mint,
          success: mint,
          amber,
          warning: amber,
          danger: red,
          page: "#F6F8FB",
          "surface-muted": "#EEF1F5", // consolidates the old bg-[#EDF0F4]/#ECEEF1/#F1F3F6/#E9EBEE one-offs
          line: "#E5E9F0",
          muted: "#64748B",
        };
      })(),
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
        display: ["Poppins", "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(16, 27, 51, 0.04), 0 1px 3px rgba(16, 27, 51, 0.06)",
        pop: "0 10px 30px rgba(16, 27, 51, 0.10)",
      },
      maxWidth: {
        shell: "1200px",
      },
    },
  },
  plugins: [],
};
