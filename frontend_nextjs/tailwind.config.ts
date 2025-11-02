import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        neon: {
          cyan: "#00FFFF",
          pink: "#FF00FF",
          purple: "#A855F7",
        },
        dark: {
          purple: "#1A0033",
          blue: "#0A0E27",
          black: "#000000",
        },
      },
      fontFamily: {
        orbitron: ["var(--font-orbitron)", "sans-serif"],
        inter: ["var(--font-inter)", "sans-serif"],
      },
      boxShadow: {
        neon: "0 0 10px #00FFFF, 0 0 20px #00FFFF, 0 0 30px #00FFFF",
        "neon-pink": "0 0 10px #FF00FF, 0 0 20px #FF00FF, 0 0 30px #FF00FF",
        "neon-purple": "0 0 10px #A855F7, 0 0 20px #A855F7",
        glow: "0 0 20px rgba(0, 255, 255, 0.5)",
      },
      animation: {
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow-slow": "glow 3s ease-in-out infinite",
        float: "float 6s ease-in-out infinite",
      },
      keyframes: {
        glow: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-20px)" },
        },
      },
      backgroundImage: {
        "gradient-neon": "linear-gradient(135deg, #00FFFF 0%, #FF00FF 100%)",
        "gradient-dark": "linear-gradient(135deg, #1A0033 0%, #0A0E27 100%)",
      },
    },
  },
  plugins: [],
};
export default config;

