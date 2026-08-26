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
  allowedDevOrigins: ['goliath', 'localhost', '127.0.0.1'],
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
