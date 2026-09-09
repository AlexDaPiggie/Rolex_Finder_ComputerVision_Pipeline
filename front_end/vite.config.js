import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/predict': 'https://alexdapiggie--rolex-watch-recognizer-rolexwatchapi-web.modal.run',
    },
  },
})
