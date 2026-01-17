/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                mixer: {
                    bg: '#1a1a1a',
                    panel: '#2a2a2a',
                    fader: '#3a3a3a',
                    accent: '#00d9ff',
                    vocal: '#3b82f6',
                    drums: '#ef4444',
                    bass: '#10b981',
                    other: '#f59e0b',
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            }
        },
    },
    plugins: [],
}
