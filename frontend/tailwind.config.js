/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#000000',
        foreground: '#FFFFFF',
        card: 'rgba(255, 255, 255, 0.03)',
        'card-foreground': '#FFFFFF',
        primary: '#FF5B9E',
        'primary-foreground': '#FFFFFF',
        secondary: '#34B3D2',
        'secondary-foreground': '#FFFFFF',
        accent: '#C865D4',
        'accent-foreground': '#FFFFFF',
        muted: 'rgba(255, 255, 255, 0.1)',
        'muted-foreground': 'rgba(255, 255, 255, 0.7)',
        border: 'rgba(255, 255, 255, 0.1)',
        input: 'rgba(255, 255, 255, 0.05)',
        ring: '#FF5B9E',
      },
      fontFamily: {
        heading: ['Space Grotesk', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-main': 'linear-gradient(135deg, #FF5B9E 0%, #C865D4 25%, #8B71E0 50%, #34B3D2 100%)',
        'gradient-button': 'linear-gradient(90deg, #F74AC1 0%, #74E8FF 100%)',
        'gradient-card': 'linear-gradient(135deg, rgba(255, 91, 158, 0.1) 0%, rgba(52, 179, 210, 0.1) 100%)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};