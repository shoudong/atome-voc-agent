/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        pink: {
          50: '#FFF1F5',
          100: '#FFD9E4',
          300: '#FF8AAE',
          500: '#F0356A',
          600: '#D81E56',
          700: '#B21548',
        },
        sev: {
          s0: '#9CA3AF',
          s1: '#10B981',
          s2: '#F59E0B',
          s3: '#F97316',
          s4: '#DC2626',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Inter', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        sm: '0 1px 2px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.06)',
        md: '0 4px 12px rgba(15,23,42,0.06), 0 2px 4px rgba(15,23,42,0.04)',
      },
      borderRadius: {
        sm: '6px',
        md: '10px',
        lg: '14px',
      },
    },
  },
  plugins: [],
};
