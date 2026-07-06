import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // In production, /api/extract is served by the Vercel Python function
  // (api/extract.py). For local development, proxy it to the local dev
  // server (python devserver.py) so the full flow works under `next dev`.
  async rewrites() {
    if (process.env.NODE_ENV !== "development") return [];
    return [
      { source: "/api/extract", destination: "http://127.0.0.1:8000/api/extract" },
    ];
  },
};

export default nextConfig;
