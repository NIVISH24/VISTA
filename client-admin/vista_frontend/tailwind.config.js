/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        armyGreen: "#4B5320",
        militaryOlive: "#6E6E3A",
        darkCamouflage: "#2C2C2C",
        highlightRed: "#FF5E5B",
        lightBlack: "#1a1a1a",
      },
      fontFamily: {
        geist: ["var(--font-geist-sans)", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};
