/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        void: "#0A0E12",
        panel: "#12181F",
        "panel-raised": "#161D25",
        line: "#232B35",
        "line-soft": "#1A2129",
        ink: "#E8EDF2",
        "ink-muted": "#7C8894",
        signal: "#D9A441",
        "signal-dim": "#8A6B32",
        sev: {
          critical: "#E5484D",
          high: "#F2994A",
          medium: "#F2C94C",
          low: "#56CCF2",
          info: "#5B6572",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      borderRadius: {
        DEFAULT: "4px",
      },
    },
  },
  plugins: [],
};
