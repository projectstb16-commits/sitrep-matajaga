import { readFile, readdir } from "node:fs/promises";
import path from "node:path";

import type { ArchiveIndex, Sitrep } from "@/types/sitrep";

/**
 * Pembacaan SITREP dari arsip.
 *
 * Dashboard tidak membaca DOCX dan tidak menghitung ulang risiko. Yang dibaca
 * adalah JSON hasil `mjs-ingest`, yang sudah lolos skema dan aturan doktrin.
 * Pemisahan itu disengaja: satu-satunya tempat angka risiko ditetapkan adalah
 * jalur produksi, sehingga viewer tidak dapat menghasilkan angka yang berbeda
 * dari dokumen terbit.
 */

const REPO_ROOT = path.resolve(process.cwd(), "..");

/** Folder arsip. Dapat diarahkan ke folder produksi lewat MJS_ARCHIVE_DIR. */
export const ARCHIVE_DIR =
  process.env.MJS_ARCHIVE_DIR ?? path.join(REPO_ROOT, "data", "sitreps");

const EXAMPLE = path.join(REPO_ROOT, "schema", "example.sitrep.json");

export class ArchiveEmpty extends Error {}

/** Daftar edisi yang tersedia, terbaru lebih dahulu. */
export async function listEditions(): Promise<string[]> {
  let entries: string[];
  try {
    entries = await readdir(ARCHIVE_DIR);
  } catch {
    return [];
  }
  return entries
    .filter((name) => name.endsWith(".json") && !name.startsWith("."))
    .map((name) => name.replace(/\.json$/, ""))
    .sort()
    .reverse();
}

/** Baca indeks arsip bila `mjs-ingest index` sudah pernah dijalankan. */
export async function readIndex(): Promise<ArchiveIndex | null> {
  try {
    const raw = await readFile(path.join(ARCHIVE_DIR, "index.json"), "utf8");
    return JSON.parse(raw) as ArchiveIndex;
  } catch {
    return null;
  }
}

export async function readSitrep(editionId: string): Promise<Sitrep> {
  const safe = path.basename(editionId);
  const raw = await readFile(path.join(ARCHIVE_DIR, `${safe}.json`), "utf8");
  return JSON.parse(raw) as Sitrep;
}

/**
 * Edisi terbaru pada arsip.
 *
 * Arsip yang masih kosong mengembalikan contoh skema, dan `isExample`
 * menandainya agar antarmuka menyatakannya terang-terangan. Menampilkan
 * contoh sebagai edisi nyata akan menjadikan nol pada setiap pilar terbaca
 * sebagai penilaian risiko, bukan sebagai ketiadaan data.
 */
export async function readLatest(): Promise<{ sitrep: Sitrep; isExample: boolean }> {
  const editions = await listEditions();
  const latest = editions.find((id) => id !== "index");

  if (latest) {
    return { sitrep: await readSitrep(latest), isExample: false };
  }

  const raw = await readFile(EXAMPLE, "utf8");
  return { sitrep: JSON.parse(raw) as Sitrep, isExample: true };
}
