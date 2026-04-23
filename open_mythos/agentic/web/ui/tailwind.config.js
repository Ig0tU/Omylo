/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        obsidian: '#050505',
        cybercyan: '#00f5ff',
        mythosgold: '#d4af37',
      },
    },
  },
  plugins: [],
}
