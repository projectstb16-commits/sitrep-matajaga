/**
 * Tipe SITREP, turunan langsung dari schema/sitrep.schema.json.
 *
 * Skema JSON adalah kontrak tunggal antara ingest (Python) dan viewer ini.
 * Bila skema berubah, berkas ini wajib menyusul pada commit yang sama.
 */

export type ClaimTag = "FACT" | "ANALYSIS" | "ASSUMPTION";

export type Horizon = "0-6h" | "0-24h" | "0-72h" | "0-30d";

export type Reliability = "A1" | "B2" | "B3" | "C3";

export type Classification = "PREVIEW_OPEN_REDISTRIBUTION" | "CLIENT_TIER_A";

export type PillarKey = "security" | "transport" | "economy" | "cyber" | "weather";

export interface Claim {
  text: string;
  tag: ClaimTag;
  source_ids?: string[];
}

export interface Edition {
  id: string;
  date: string;
  sequence: number;
  classification: Classification;
  tier: "A" | "B";
  theatre_primary?: string;
  cutoff?: string;
  methodology: "MSRM v1.1";
}

export interface Risk {
  composite: number;
  pillars: Record<PillarKey, number>;
}

export interface Zone {
  zone: string;
  score: number;
  drivers?: string[];
}

export interface Alert {
  horizon: Horizon;
  headline: string;
  detail?: string;
  score?: number;
  claim_tag: ClaimTag;
  source_ids?: string[];
}

/**
 * Klaim sebagaimana ditemukan pada data runtime.
 *
 * Skema menuntut setiap klaim bertanda, tetapi JSON yang dibaca viewer
 * berasal dari luar proses ini dan bisa saja belum lolos validasi. Tipe ini
 * menyatakan kemungkinan itu secara terbuka, sehingga antarmuka wajib
 * menanganinya alih-alih mengandaikan tanda selalu ada.
 */
export type UntaggedTolerantClaim = Omit<Claim, "tag"> & { tag?: ClaimTag };

export interface Section {
  key: string;
  title: string;
  claims: UntaggedTolerantClaim[];
}

export interface RecommendedAction {
  horizon: Horizon;
  action: string;
  rationale?: string;
}

export interface OutlookEntry {
  horizon: "H+1" | "H+2";
  claim: Claim;
}

export interface Source {
  id: string;
  reliability: Reliability;
  publisher: string;
  title?: string;
  url?: string;
  retrieved_at?: string;
}

export interface Sitrep {
  edition: Edition;
  risk: Risk;
  zones: Zone[];
  alerts: Alert[];
  sections: Section[];
  recommended_actions?: RecommendedAction[];
  outlook?: OutlookEntry[];
  sources: Source[];
}

/** Satu entri indeks arsip, keluaran `mjs-ingest index`. */
export interface EditionRecord {
  edition_id: string;
  date: string;
  sequence: number;
  brief: string | null;
  whatsapp: string | null;
  issues: string[];
}

export interface ArchiveIndex {
  generated_from: string;
  next_sequence: number;
  editions: EditionRecord[];
}

/** Satu kegiatan pada rekap kegiatan sipil. */
export interface CivilAction {
  activity_date: string | null;
  region: string | null;
  area: string | null;
  time_start: string | null;
  time_end: string | null;
  location: string | null;
  organizer: string | null;
  /** Hanya hadir bila penyertaan PII dipilih secara sadar saat ekstraksi. */
  leader?: string | null;
  crowd_reported: number | null;
  kind: "unjuk_rasa" | "giat_masyarakat" | "giat_kepolisian" | "tidak_ditentukan";
  demand: string | null;
  reported_on: string;
  source_format?: "berlabel" | "bernomor";
  issues?: string[];
}

export interface KindCount {
  actions: number;
  crowd_reported: number;
}

/**
 * Rekap kegiatan sipil, keluaran `mjs-ingest whatsapp`.
 *
 * Bukan SITREP: tidak memuat skor risiko. Jumlah massa adalah angka yang
 * dilaporkan relay, bukan penilaian penerbit.
 */
export interface CivilActionDigest {
  generated_from: "whatsapp-export";
  redacted: boolean;
  window: { from: string | null; to: string | null };
  source: { id: string; reliability: Reliability; publisher: string };
  counts: {
    actions: number;
    duplicates_merged: number;
    skipped_lines: number;
    without_crowd_figure?: number;
    by_kind: Record<string, KindCount>;
  };
  actions: CivilAction[];
  skipped?: string[];
}
