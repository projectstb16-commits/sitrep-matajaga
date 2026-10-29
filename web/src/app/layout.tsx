import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "MJ-Sentinel SITREP",
  description:
    "Viewer arsip SITREP Matajaga Research. Angka risiko ditetapkan jalur produksi, bukan oleh antarmuka ini.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
