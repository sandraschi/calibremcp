/** @type {import('next').NextConfig} */
const path = require("node:path");

const isTauri = process.env.TAURI_BUILD === "1";

const nextConfig = {
	reactStrictMode: true,
	trailingSlash: isTauri,
	...(isTauri ? { output: "export" } : { output: "standalone" }),
	images: {
		unoptimized: isTauri,
		domains: ["localhost"],
	},
	allowedDevOrigins: ["goliath", "localhost", "127.0.0.1"],
	turbopack: {
		root: path.resolve(__dirname),
	},
	async rewrites() {
		if (isTauri) return [];
		return [
			{
				source: "/api/:path*",
				destination: "http://127.0.0.1:10720/api/:path*",
			},
			{
				source: "/image/:path*",
				destination: "http://127.0.0.1:10720/image/:path*",
			},
			{
				source: "/docs",
				destination: "http://127.0.0.1:10720/docs",
			},
			{
				source: "/docs/:path*",
				destination: "http://127.0.0.1:10720/docs/:path*",
			},
			{
				source: "/openapi.json",
				destination: "http://127.0.0.1:10720/openapi.json",
			},
			{
				source: "/redoc",
				destination: "http://127.0.0.1:10720/redoc",
			},
		];
	},
};

module.exports = nextConfig;
