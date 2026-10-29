import type { NextConfig } from "next";

const config: NextConfig = {
  reactStrictMode: true,
  // Dashboard hanya membaca arsip; tidak ada jalur tulis ke folder produksi.
  experimental: {},
};

export default config;
