import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Static export for Docker deployment
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  }
};

export default nextConfig;
