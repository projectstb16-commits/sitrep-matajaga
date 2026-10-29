# Catatan kerja — sitrep-matajaga

## Sifat produk

Repositori ini menyajikan produk intelijen yang dibaca untuk mengambil keputusan operasional. Kesalahan angka atau klaim di sini bukan bug tampilan.

## Aturan yang mengikat

Aturan lengkap ada di `docs/doctrine/`. Yang paling sering dilanggar tanpa sengaja:

- **Jangan mengarang angka, nama, tanggal, kutipan, sumber, atau tautan.** Bila data tidak ada, yang ditulis adalah "Data belum tersedia". Ini berlaku pada contoh, fixture tes, dan dokumentasi, bukan hanya pada produk terbit.
- **Setiap klaim bertanda** `FACT`, `ANALYSIS`, atau `ASSUMPTION`. Tidak ada nilai bawaan. Klaim `FACT` wajib merujuk sumber yang terdaftar.
- **Label metodologi tetap** `MSRM v1.1`.
- **Tanpa emoji dan ikon dekoratif**, di kode maupun di antarmuka.
- **Tanpa penyebutan firma intelijen atau konsultan asing** pada produk apa pun. Validator menolaknya.
- **Skala risiko tetap**: Low 0–39, Moderate 40–59, High 60–79, Critical 80–100.

## Data pribadi

Repositori ini publik. Rekap relay memuat nama penanggung jawab aksi dan nomor telepon pelapor.

- Nomor telepon tidak pernah disimpan, pada bidang mana pun.
- Nama penanggung jawab disunting secara bawaan; penyertaannya menuntut `--include-pii`.
- Seluruh isi `data/sitreps/` tidak masuk version control. Jangan melonggarkan `.gitignore` itu per jenis berkas.
- Jangan menaruh cuplikan data nyata ke dalam tes, contoh, atau dokumentasi. Fixture memakai nilai "Contoh" yang jelas bukan keterangan nyata.

Rinciannya di `docs/doctrine/sumber-relay.md`.

## Jangan menurunkan skor dari data mentah

Jumlah massa pada rekap relay adalah angka yang dilaporkan, bukan skor. Jangan menulis rumus yang mengubahnya menjadi skor pilar Security. Penilaian risiko ditetapkan analis.

## Nilai yang digandakan

Ambang band dan warna isian ada di dua tempat dan wajib berubah bersamaan:

- `ingest/src/mjs_ingest/msrm.py`
- `web/src/lib/bands.ts`

Begitu pula `schema/sitrep.schema.json` dengan `web/src/types/sitrep.ts`.

## Warna tidak membawa band sendirian

Isian band yang ditetapkan brand standard tidak terpisah cukup jauh untuk dibedakan dengan andal — HIGH dan CRITICAL hanya berjarak ΔE 4.2 pada penglihatan normal. Setiap penanda band wajib menuliskan skor dan nama band sebagai teks. Jangan membuat komponen yang mengandalkan warna saja. Rinciannya di `docs/doctrine/brand-standard.md`.

## Sebelum menyatakan selesai

```bash
cd ingest && python3 -m pytest
```

```bash
cd web && npm run typecheck && npm run lint && npm run build
```
