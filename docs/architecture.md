# Arsitektur

## Pembagian tanggung jawab

```
arsip terbit (DOCX + TXT)
        |
        |  mjs-ingest parse / index          Python
        v
  SITREP JSON  <-  schema/sitrep.schema.json   (kontrak tunggal)
        |
        |  mjs-ingest validate                Python
        v
   dashboard                                  TypeScript / Next.js
```

Dua bahasa dipakai karena dua pekerjaan yang berbeda sifatnya. Pembacaan dan validasi dokumen terbit adalah pekerjaan batch yang berdekatan dengan jalur produksi DOCX; penyajian adalah pekerjaan antarmuka. Yang menyatukan keduanya satu berkas skema, bukan konvensi tak tertulis.

## Aturan yang dijaga pembagian ini

**Dashboard tidak menghitung risiko.** Viewer membaca skor, memetakannya ke band, lalu menampilkannya. Viewer tidak pernah menurunkan komposit sendiri. Bila angka di layar berbeda dari angka pada dokumen terbit, pembaca menghadapi dua penilaian atas satu edisi dan tidak ada cara memastikan mana yang benar. Perhitungan hanya ada di `ingest/src/mjs_ingest/msrm.py`.

**Dashboard tidak menulis ke arsip.** Arsip adalah keluaran jalur produksi. `archive.scan` hanya membaca.

**Nilai yang digandakan dijaga berpasangan.** Ambang band dan warna isian muncul di dua tempat: `ingest/src/mjs_ingest/msrm.py` dan `web/src/lib/bands.ts`. Keduanya wajib berubah pada commit yang sama. Pemisahan proses memaksa penggandaan ini; yang tidak boleh terjadi adalah keduanya menyimpang tanpa disadari.

## Lapisan validasi

Ada dua, dan keduanya diperlukan:

1. **Skema JSON** menjaga bentuk — tipe, bidang wajib, enum, pola `MJS-YYYY-MM-DD-NNN`.
2. **Aturan doktrin** (`validate.py`) menjaga hal yang tidak dapat dinyatakan skema — klaim `FACT` harus merujuk sumber yang benar-benar terdaftar, komposit harus konsisten dengan pilarnya, klasifikasi harus sesuai tier, dan tidak ada penyebutan terlarang.

Validator mengembalikan daftar temuan, bukan melempar pengecualian pada temuan pertama, sehingga penyusun melihat seluruh masalah dalam satu lintasan.

## Aturan pengaman komposit

Rata-rata berbobot dapat meredam satu pilar ekstrem sampai menyesatkan. Pilar cuaca pada 85 (CRITICAL) dengan empat pilar lain rendah menghasilkan rata-rata berbobot 28, yaitu band LOW. Karena itu berlaku aturan: bila ada pilar pada band CRITICAL, komposit tidak dilaporkan di bawah ambang HIGH, dan pilar yang memicunya dicatat pada `Composite.floored_by` agar keputusan itu dapat diaudit alih-alih tersembunyi di dalam satu angka. Validator melaporkannya sebagai peringatan, bukan kesalahan.

## Yang belum dikerjakan

- Ekstraksi tabel Risk Dashboard dari DOCX. `parse_docx` baru membaca heading dan paragraf; angka pilar belum terbaca dan sengaja dibiarkan kosong, bukan diisi nilai bawaan.
- Halaman arsip (daftar seluruh edisi) dan halaman per edisi. Saat ini dashboard menampilkan edisi terbaru saja.
- Peta zona sebagai geografi. Regional risk map masih berupa tabel terurut.
- Bobot komposit masih provisional; lihat `docs/doctrine/msrm-v1.1.md`.
