/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a',
        }
      },
      fontFamily: {
        'arabic': ['Noto Sans Arabic', 'system-ui', 'sans-serif'],
        'hebrew': ['Noto Sans Hebrew', 'system-ui', 'sans-serif'],
        'english': ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
      }
    },
  },
  plugins: [
    // RTL support
    function({ addUtilities }) {
      const newUtilities = {
        '.start-0': {
          'inset-inline-start': '0',
        },
        '.start-4': {
          'inset-inline-start': '1rem',
        },
        '.end-0': {
          'inset-inline-end': '0',
        },
        '.end-4': {
          'inset-inline-end': '1rem',
        },
        '.ms-auto': {
          'margin-inline-start': 'auto',
        },
        '.me-auto': {
          'margin-inline-end': 'auto',
        },
        '.ms-4': {
          'margin-inline-start': '1rem',
        },
        '.me-4': {
          'margin-inline-end': '1rem',
        },
      };
      addUtilities(newUtilities);
    }
  ],
};