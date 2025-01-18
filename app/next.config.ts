import type { NextConfig } from "next";
import { config } from 'dotenv';

config({ path: '../.env' });

const nextConfig: NextConfig = {
  /* config options here */
  env: {
    LOCAL: process.env.LOCAL,
    SUPABASE_URL: process.env.LOCAL ?
      process.env.SUPABASE_URL :
      process.env.SUPABASE_LOCAL_URL,
    SUPABASE_KEY: process.env.LOCAL ?
      process.env.SUPABASE_KEY :
      process.env.SUPABASE_LOCAL_KEY,
  },
  rewrites: async () => {
    return [
      {
        source: "/api/:path*",
        destination:
          process.env.NODE_ENV === "development"
            ? "http://127.0.0.1:8000/api/:path*"
            : "/api/",
      },
    ];
  }
};

export default nextConfig;
