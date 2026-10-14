import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// Tailwind v4 нь Vite plugin-ээр ажиллана
export default defineConfig({
  plugins: [react(), tailwindcss()],
})
