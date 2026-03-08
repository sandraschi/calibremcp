/** @type {import('next').NextConfig} */
const path = require('path');

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
    ];
  },
};

module.exports = nextConfig;
