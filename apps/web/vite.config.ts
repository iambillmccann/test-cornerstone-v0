import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'node:path'

const appSlug = process.env.VITE_APP_SLUG || 'cornerstone'
const appDisplayName = process.env.VITE_APP_DISPLAY_NAME || 'Cornerstone'
const appDescription = process.env.VITE_APP_DESCRIPTION || `${appDisplayName} SaaS template`

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icons/icon-192.svg', 'icons/icon-512.svg', 'icons/icon-maskable.svg'],
      manifest: {
        name: appDisplayName,
        short_name: appDisplayName,
        description: appDescription,
        theme_color: '#111111',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192.svg',
            sizes: '192x192',
            type: 'image/svg+xml',
          },
          {
            src: '/icons/icon-512.svg',
            sizes: '512x512',
            type: 'image/svg+xml',
          },
          {
            src: '/icons/icon-maskable.svg',
            sizes: '512x512',
            type: 'image/svg+xml',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        navigateFallbackDenylist: [/^\/api\//],
        runtimeCaching: [
          {
            urlPattern: ({ url }) =>
              url.pathname.startsWith('/api/') ||
              url.hostname.includes('clerk') ||
              url.pathname.startsWith('/sign-in') ||
              url.pathname.startsWith('/sign-up') ||
              url.pathname.startsWith('/sso-callback'),
            handler: 'NetworkOnly',
          },
          {
            urlPattern: ({ request, url }) =>
              request.destination === 'style' ||
              request.destination === 'script' ||
              request.destination === 'worker' ||
              request.destination === 'font' ||
              request.destination === 'image' ||
              url.pathname.startsWith('/assets/'),
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: `${appSlug}-static-assets`,
              expiration: {
                maxEntries: 200,
                maxAgeSeconds: 60 * 60 * 24 * 30,
              },
            },
          },
          {
            urlPattern: ({ request, url }) =>
              request.mode === 'navigate' && !url.pathname.startsWith('/api/'),
            handler: 'NetworkFirst',
            options: {
              cacheName: `${appSlug}-pages`,
              networkTimeoutSeconds: 3,
              expiration: {
                maxEntries: 30,
                maxAgeSeconds: 60 * 60 * 24,
              },
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
