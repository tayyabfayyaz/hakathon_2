import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker/Kubernetes deployment
  output: "standalone",
};

export default nextConfig;
