/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./lapmarkaz_app/**/*.html",
    "./lapmarkaz_app/**/*.py",
    "./lapmarkaz_app/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#0B5FD5",
          50: "#EFF5FE",
          100: "#DCE9FC",
          600: "#0B5FD5",
          700: "#0A4FB4",
          800: "#083D8C",
        },
        ink: "#0F172A",
        navy: {
          DEFAULT: "#101B33",
          800: "#16233F",
          700: "#1E2C4A",
        },
        mint: {
          DEFAULT: "#35D6A4",
          600: "#25BB8C",
        },
        page: "#F6F8FB",
        line: "#E5E9F0",
        muted: "#64748B",
      },
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
