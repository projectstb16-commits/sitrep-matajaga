import { FlatCompat } from "@eslint/eslintrc";

const compat = new FlatCompat();

// next-env.d.ts dihasilkan Next dan tidak dirawat tangan; aturan gaya tidak
// berlaku atasnya.
const config = [
  { ignores: [".next/**", "node_modules/**", "next-env.d.ts"] },
  ...compat.extends("next/core-web-vitals", "next/typescript"),
];

export default config;
