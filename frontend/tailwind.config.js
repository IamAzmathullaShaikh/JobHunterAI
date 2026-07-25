export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: '#0B1220',
        panel: '#0F172A',
        primary: '#7C3AED',
        'primary-dark': '#6B21A8',
        accent: '#06B6D4',
        muted: '#94A3B8',
        error: '#EF4444'
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
      }
    }
  },
  plugins: []
}
