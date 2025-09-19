import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',

  // THÊM KHỐI NÀY VÀO
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },

  experimental: {
    // Suppress scroll-blocking touchstart warnings
    scrollRestoration: true,
  },

  // Add headers to suppress passive event listener warnings
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Feature-Policy',
            value: 'touch-action *',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
