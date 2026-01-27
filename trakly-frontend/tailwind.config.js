/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        status: {
          new: '#6b7280',
          in_progress: '#3b82f6',
          review: '#f59e0b',
          done: '#10b981',
          closed: '#64748b',
          wont_fix: '#ef4444',
        },
        severity: {
          blocker: '#7f1d1d',
          critical: '#b91c1c',
          major: '#ea580c',
          minor: '#f59e0b',
          trivial: '#6b7280',
        },
        priority: {
          critical: '#dc2626',
          high: '#ea580c',
          medium: '#3b82f6',
          low: '#6b7280',
        },
      },
    },
  },
  plugins: [],
}
