/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './dashboard/**/*.py',
    './static/js/**/*.js'
  ],
  theme: {
    extend: {
      colors: {
        'undp-blue': '#0066CC',
        'undp-blue-dark': '#004499',
        'undp-blue-light': '#3385D6',
        'undp-white': '#FFFFFF',
        'undp-gray': '#F5F5F5',
        'undp-gray-dark': '#E0E0E0',
        'undp-text': '#333333',
        'undp-text-light': '#666666',
        'success': '#28A745',
        'warning': '#FFC107',
        'danger': '#DC3545',
        'info': '#17A2B8'
      }
    }
  },
  plugins: []
}


