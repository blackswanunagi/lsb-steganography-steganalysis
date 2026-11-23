import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Served from https://blackswanunagi.github.io/lsb-steganography-steganalysis/
  base: process.env.GITHUB_PAGES ? '/lsb-steganography-steganalysis/' : '/',
})
