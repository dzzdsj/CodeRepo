/** @type {import('tailwindcss').Config} */

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    container: {
      center: true,
    },
    extend: {
      colors: {
        // 金融深色主题色板
        base: {
          900: "#0B0E11", // 主背景（近黑）
          800: "#0E1217", // 次主背景
          700: "#161A1F", // 次级面板
          600: "#1E2329", // 卡片/悬停
          500: "#2B3138", // 边框/分隔
          400: "#3A4049", // 更亮边框
        },
        accent: {
          DEFAULT: "#F0B90B", // 强调金黄
          hover: "#FFD025",
          muted: "#8C6E0A",
        },
        up: "#F6465D", // A股红涨
        down: "#16C784", // 跌绿
        flat: "#848E9C", // 平
      },
      fontFamily: {
        sans: [
          "Noto Sans SC",
          "PingFang SC",
          "HarmonyOS Sans SC",
          "-apple-system",
          "Segoe UI",
          "sans-serif",
        ],
        mono: ["JetBrains Mono", "SF Mono", "Menlo", "monospace"],
      },
      boxShadow: {
        card: "0 1px 0 rgba(255,255,255,0.02) inset, 0 8px 24px rgba(0,0,0,0.45)",
        glow: "0 0 0 1px rgba(240,185,11,0.35), 0 0 24px rgba(240,185,11,0.15)",
      },
      keyframes: {
        flashUp: {
          "0%": { backgroundColor: "rgba(246,70,93,0.35)" },
          "100%": { backgroundColor: "transparent" },
        },
        flashDown: {
          "0%": { backgroundColor: "rgba(22,199,132,0.35)" },
          "100%": { backgroundColor: "transparent" },
        },
        slideInRight: {
          "0%": { transform: "translateX(120%)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
      },
      animation: {
        "flash-up": "flashUp 0.6s ease-out",
        "flash-down": "flashDown 0.6s ease-out",
        "slide-in-right": "slideInRight 0.3s ease-out",
      },
    },
  },
  plugins: [],
};
