/** @type {import('next').NextConfig} */
const path = require('node:path');

const isTauri = process.env.TAURI_BUILD === '1';

const nextConfig = {
  reactStrictMode: true,
  trailingSlash: isTauri,
  // basePath '/app' is REQUIRED for the Tauri NSIS installer: the backend serves
  // this static export as an SPA mounted at /app, so all asset/page URLs must be
  // prefixed /app/_next/..., /app/books, etc. (webview navigates to
  // http://127.0.0.1:10720/app/). Files stay at out/ root but reference /app/...
  // Do NOT remove it - without it assets resolve to /_next/ and 404 under the /app mount.
  ...(isTauri ? { output: 'export', basePath: '/app' } : { output: 'standalone' }),
  images: {
    unoptimized: isTauri,
    domains: ['localhost'],
  },
  // LAN / Tailscale dev access: Next.js blocks cross-host page loads without an
  // explicit allow-list. Extra hosts via CALIBRE_DEV_ORIGINS (comma-separated,
  // e.g. "192.168.1.10,goliath.tail12345.ts.net"). webapp/start-lan.ps1 sets it
  // automatically from detected interface addresses.
  allowedDevOrigins: [
    'goliath',
    'localhost',
    '127.0.0.1',
    ...(process.env.CALIBRE_DEV_ORIGINS
      ? process.env.CALIBRE_DEV_ORIGINS.split(',')
          .map((s) => s.trim())
          .filter(Boolean)
      : []),
  ],
  turbopack: {
    root: path.resolve(__dirname),
  },
  async rewrites() {
    if (isTauri) return [];
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:10720/api/:path*',
      },
      {
        source: '/image/:path*',
        destination: 'http://127.0.0.1:10720/image/:path*',
      },
      {
        source: '/docs',
        destination: 'http://127.0.0.1:10720/docs',
      },
      {
        source: '/docs/:path*',
        destination: 'http://127.0.0.1:10720/docs/:path*',
      },
      {
        source: '/openapi.json',
        destination: 'http://127.0.0.1:10720/openapi.json',
      },
      {
        source: '/redoc',
        destination: 'http://127.0.0.1:10720/redoc',
      },
    ];
  },
};

module.exports = nextConfig;
