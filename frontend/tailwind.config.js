/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#0F0F0F',
        foreground: '#F5F5F5',
        card: '#1A1A1A',
        'card-foreground': '#F5F5F5',
        primary: '#8B5CF6',
        'primary-foreground': '#FFFFFF',
        secondary: '#252525',
        'secondary-foreground': '#A1A1AA',
        accent: '#7C3AED',
        'accent-foreground': '#FFFFFF',
        muted: '#2A2A2A',
        'muted-foreground': '#9CA3AF',
        border: '#2A2A2A',
        input: '#252525',
        ring: '#8B5CF6',
      },
      fontFamily: {
        heading: ['Space Grotesk', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        lg: '0.75rem',
        md: '0.5rem',
        sm: '0.375rem',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};