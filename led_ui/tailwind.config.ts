import { type Config } from "tailwindcss";
import { fontFamily } from "tailwindcss/defaultTheme";

export default {
  content: ["./src/**/*.tsx"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", ...fontFamily.sans],
      },
      gridTemplateColumns: {
        // 24 column grid
        '24': 'repeat(24, minmax(0, 1fr))',
      },
    },
  },
  plugins: [],
} satisfies Config;
