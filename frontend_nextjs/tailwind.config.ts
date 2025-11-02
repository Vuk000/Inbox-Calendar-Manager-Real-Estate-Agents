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
          blue: "#00FFFF",
        },
        dark: {
          purple: "#1A0033",
          blue: "#0A0E27",
          black: "#000000",
          bg: "#0A001A",
        },
        cyberpunk: {
          blue: "#00FFFF",
          purple: "#A020F0",
          pink: "#FF00FF",
          cyan: "#00FFFF",
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
        "neon-glow-blue": "0 0 10px #00FFFF, 0 0 20px #00FFFF, 0 0 30px #00FFFF, 0 0 40px #00FFFF",
        "neon-glow-purple": "0 0 10px #A020F0, 0 0 20px #A020F0, 0 0 30px #A020F0, 0 0 40px #A020F0",
        "neon-glow-pink": "0 0 10px #FF00FF, 0 0 20px #FF00FF, 0 0 30px #FF00FF, 0 0 40px #FF00FF",
      },
      animation: {
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow-slow": "glow 3s ease-in-out infinite",
        float: "float 6s ease-in-out infinite",
        "pulse-neon": "pulse-neon 2s ease-in-out infinite",
        "glow-sweep": "glow-sweep 3s ease-in-out infinite",
        holographic: "holographic 4s ease-in-out infinite",
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
        "pulse-neon": {
          "0%, 100%": { opacity: "1", filter: "brightness(1)" },
          "50%": { opacity: "0.8", filter: "brightness(1.5)" },
        },
        "glow-sweep": {
          "0%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
          "100%": { backgroundPosition: "0% 50%" },
        },
        holographic: {
          "0%, 100%": { filter: "hue-rotate(0deg) brightness(1)" },
          "50%": { filter: "hue-rotate(90deg) brightness(1.2)" },
        },
      },
      backgroundImage: {
        "gradient-neon": "linear-gradient(135deg, #00FFFF 0%, #FF00FF 100%)",
        "gradient-dark": "linear-gradient(135deg, #1A0033 0%, #0A0E27 100%)",
        "cyberpunk-gradient": "linear-gradient(135deg, #0A001A 0%, #1A0033 50%, #0A0E27 100%)",
        "dark-gradient": "linear-gradient(180deg, #0A001A 0%, #000000 100%)",
      },
    },
  },
  plugins: [],
};
export default config;

