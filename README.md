# sitrep-matajaga

Dashboard viewer untuk arsip SITREP MJ-Sentinel — Matajaga Research, PT HRM Multi Sinergy.

Repositori ini **menyajikan** SITREP; ia tidak memproduksinya. Produksi brief tetap berjalan pada jalur yang ada dan menghasilkan dua berkas per edisi: DOCX bahasa Inggris dan TXT bahasa Indonesia untuk WhatsApp. Yang dikerjakan di sini adalah membaca arsip itu, memvalidasinya terhadap doktrin, dan menampilkannya.

## Struktur

| Direktori | Isi |
|---|---|
| `schema/` | `sitrep.schema.json` — kontrak data tunggal antara ingest dan viewer, beserta satu contoh |
| `ingest/` | Paket Python `mjs_ingest`: pembacaan arsip, ekstraksi DOCX, perhitungan MSRM, validasi doktrin |
| `web/` | Dashboard Next.js (App Router, TypeScript, Tailwind) |
| `docs/doctrine/` | Aturan yang mengikat produk: MSRM v1.1, brand standard, klasifikasi, penomoran edisi, sumber relay dan data pribadi |
| `docs/architecture.md` | Pembagian tanggung jawab antara kedua sisi dan alasannya |
| `data/sitreps/` | Arsip lokal. Seluruh isinya tidak masuk version control |
| `data/gazetteer.json` | Koordinat titik aksi beserta sumbernya. Entri tanpa koordinat tetap diperingkat |

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

Ekstraksi rekap rengiat dari ekspor chat relay menjadi rekap kegiatan sipil:

```bash
mjs-ingest whatsapp "<ekspor.txt>" --publisher "<nama relay>" -o data/sitreps/civil-action-digest.json
```

Potongan SITREP untuk satu edisi, berisi alert dan satu bagian isi:

```bash
mjs-ingest whatsapp "<ekspor.txt>" --fragment-for 2026-10-28
```

Analisis lengkap — peringkat titik, pola berulang, penumpukan, dan laporan lapangan:

```bash
mjs-ingest analyse "<ekspor.txt>" --update-gazetteer -o data/sitreps/analysis.json
```

Dashboard menampilkan rekap begitu `civil-action-digest.json` ada di folder arsip, dan halaman overview lengkap begitu `analysis.json` ada.

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

Peta sebaran titik hanya menempatkan titik yang berkoordinat, dan koordinat tanpa sumber tidak dicatat. Pemetaan rencana terhadap kejadian menghitung berapa rencana yang memiliki laporan lapangan, bukan tingkat realisasi: grup relay melaporkan sebagian kecil kegiatan saja.

Rekap relay tidak diubah menjadi skor risiko. Jumlah massa yang tercantum adalah angka yang dilaporkan, dan penilaian pilar tetap pekerjaan analis. Rekap juga memuat data pribadi: nomor telepon tidak pernah disimpan, nama penanggung jawab disunting secara bawaan, dan seluruh isi `data/sitreps/` tidak masuk version control karena repositori ini publik. Dasarnya di `docs/doctrine/sumber-relay.md`.
