import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone mode for Docker deployment
  output: 'standalone',
  images: {
    unoptimized: true
  }
};

export default nextConfig;
