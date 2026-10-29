# sitrep-matajaga

Dashboard viewer untuk arsip SITREP MJ-Sentinel — Matajaga Research, PT HRM Multi Sinergy.

Repositori ini **menyajikan** SITREP; ia tidak memproduksinya. Produksi brief tetap berjalan pada jalur yang ada dan menghasilkan dua berkas per edisi: DOCX bahasa Inggris dan TXT bahasa Indonesia untuk WhatsApp. Yang dikerjakan di sini adalah membaca arsip itu, memvalidasinya terhadap doktrin, dan menampilkannya.

## Struktur

| Direktori | Isi |
|---|---|
| `schema/` | `sitrep.schema.json` — kontrak data tunggal antara ingest dan viewer, beserta satu contoh |
| `ingest/` | Paket Python `mjs_ingest`: pembacaan arsip, ekstraksi DOCX, perhitungan MSRM, validasi doktrin |
| `web/` | Dashboard Next.js (App Router, TypeScript, Tailwind) |
| `docs/doctrine/` | Aturan yang mengikat produk: MSRM v1.1, brand standard, klasifikasi, penomoran edisi |
| `docs/architecture.md` | Pembagian tanggung jawab antara kedua sisi dan alasannya |
| `data/sitreps/` | Arsip lokal. Berkas terbit tidak masuk version control |

## Menjalankan

Dashboard:

```bash
cd web && npm install && npm run dev
```

Arahkan ke folder arsip produksi lewat variabel lingkungan bila perlu:

```bash
MJS_ARCHIVE_DIR="/path/ke/01_Daily Brief" npm run dev
```

Selama arsip kosong, dashboard menampilkan `schema/example.sitrep.json` dan menyatakan secara terbuka bahwa itu contoh bentuk data, bukan penilaian risiko.

Ingest:

```bash
cd ingest && pip install -e ".[docx,schema,dev]"
```

## Perintah

```bash
mjs-ingest validate <sitrep.json>
```

```bash
mjs-ingest index "<folder arsip>" -o data/sitreps/index.json
```

```bash
mjs-ingest parse "<MJS-YYYY-MM-DD-NNN-PREVIEW-EN.docx>"
```

## Pemeriksaan

```bash
cd ingest && python3 -m pytest
```

```bash
cd web && npm run typecheck && npm run lint && npm run build
```

## Batasan yang disengaja

Dashboard tidak menghitung ulang skor risiko dan tidak menulis apa pun ke arsip. Satu-satunya tempat komposit ditetapkan adalah `ingest/src/mjs_ingest/msrm.py`. Alasannya ada di `docs/architecture.md`.

Bobot komposit yang terpasang bersifat provisional: doktrin MSRM v1.1 menetapkan skala dan daftar pilar, tetapi tidak menetapkan bobot. Angka yang dipakai dapat dikonfigurasi dan menunggu konfirmasi penerbit.
