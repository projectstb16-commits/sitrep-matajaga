/**
 * Band risiko MSRM v1.1 dan token merek.
 *
 * Nilai di sini wajib identik dengan ingest/src/mjs_ingest/msrm.py. Dokumen
 * terbit dan dashboard harus menampilkan band yang sama dengan warna yang sama;
 * dua sumber kebenaran yang menyimpang akan membuat pembaca menyimpulkan
 * tingkat risiko yang berbeda dari satu edisi yang sama.
 */

export const BRAND = {
  navy: "#0B1B3B",
  gold: "#B8860B",
} as const;

export type Band = "LOW" | "MODERATE" | "HIGH" | "CRITICAL";

/** Batas bawah inklusif per band, urut menurun. */
const BAND_FLOORS: ReadonlyArray<readonly [number, Band]> = [
  [80, "CRITICAL"],
  [60, "HIGH"],
  [40, "MODERATE"],
  [0, "LOW"],
];

export const BAND_FILL: Record<Band, string> = {
  LOW: "#DDEFD5",
  MODERATE: "#FBF2CC",
  HIGH: "#FADFC5",
  CRITICAL: "#F7D3D3",
};

/** Teks pada isian band; dipilih agar kontras tetap terbaca di cetak dan layar. */
export const BAND_INK: Record<Band, string> = {
  LOW: "#1E3F14",
  MODERATE: "#4A3A05",
  HIGH: "#5A2E06",
  CRITICAL: "#5E1111",
};

export const BAND_LABEL: Record<Band, string> = {
  LOW: "Low",
  MODERATE: "Moderate",
  HIGH: "High",
  CRITICAL: "Critical",
};

export class ScoreOutOfRange extends Error {}

export function bandOf(score: number): Band {
  if (!Number.isInteger(score) || score < 0 || score > 100) {
    throw new ScoreOutOfRange(`skor di luar rentang 0-100: ${score}`);
  }
  for (const [floor, band] of BAND_FLOORS) {
    if (score >= floor) {
      return band;
    }
  }
  throw new Error("unreachable: BAND_FLOORS harus mencakup 0");
}

export function fillOf(score: number): string {
  return BAND_FILL[bandOf(score)];
}

export function inkOf(score: number): string {
  return BAND_INK[bandOf(score)];
}

export const PILLAR_LABEL = {
  security: "Security",
  transport: "Transport",
  economy: "Economy",
  cyber: "Cyber",
  weather: "Weather",
} as const;

export const CLASSIFICATION_LABEL = {
  PREVIEW_OPEN_REDISTRIBUTION: "PREVIEW — OPEN REDISTRIBUTION",
  CLIENT_TIER_A: "CLIENT EDITION — TIER A",
} as const;
