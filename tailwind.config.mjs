/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
  theme: {
    extend: {
      colors: {
        /* Pastel palette — study-friendly, WCAG AA contrast on #e8f5e9 etc. */
        pastel: {
          mint: "#e8f5e9",
          lavender: "#f3e5f5",
          peach: "#fff3e0",
          powder: "#e3f2fd",
        },
        brand: {
          50: "#e3f2fd",
          100: "#bbdefb",
          200: "#90caf9",
          300: "#64b5f6",
          400: "#42a5f5",
          500: "#1e88e5",
          600: "#1976d2",
          700: "#1565c0",
          800: "#0d47a1",
          900: "#0a3d91",
        },
        accent: {
          50: "#fff3e0",
          100: "#ffe0b2",
          200: "#ffcc80",
          300: "#ffb74d",
          400: "#ffa726",
          500: "#ff9800",
          600: "#fb8c00",
          700: "#f57c00",
          800: "#ef6c00",
          900: "#e65100",
        },
      },
      fontFamily: {
        sans: ['"Outfit"', "system-ui", "sans-serif"],
        display: ['"Outfit"', "system-ui", "sans-serif"],
      },
      fontSize: {
        base: ["1rem", { lineHeight: "1.6" }],
      },
    },
  },
  plugins: [],
};
