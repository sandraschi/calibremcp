/** @type {import('next').NextConfig} */
const path = require('node:path');

const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  images: {
    domains: ['localhost'],
  },
  allowedDevOrigins: ['goliath', 'localhost', '127.0.0.1'],
  turbopack: {
    root: path.resolve(__dirname),
  },
  async rewrites() {
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
        // Proxy Swagger UI through Next.js so the /api-docs iframe works same-origin
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
