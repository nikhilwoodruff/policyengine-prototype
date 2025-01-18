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
  }
};

export default nextConfig;
