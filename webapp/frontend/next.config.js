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
};

module.exports = nextConfig;
