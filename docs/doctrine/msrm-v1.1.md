# MSRM v1.1 — Matajaga Strategic Risk Model

Label metodologi yang dipakai pada seluruh produk MJ-Sentinel. Nama lain tidak digunakan.

## Skala risiko

| Band | Rentang | Pengertian operasional |
|---|---|---|
| LOW | 0–39 | Operasi normal. Tidak ada pembatasan pergerakan. |
| MODERATE | 40–59 | Perlu kewaspadaan terjadwal. Rute dan jadwal ditinjau harian. |
| HIGH | 60–79 | Pembatasan selektif. Aktivitas non-esensial di zona terdampak ditunda. |
| CRITICAL | 80–100 | Pembatasan menyeluruh pada zona terdampak. Eskalasi ke pengambil keputusan. |

Batas band bersifat inklusif pada kedua ujung (`60` sudah HIGH, bukan MODERATE).

## Pilar penilaian

Lima pilar dinilai independen pada skala 0–100, lalu diringkas menjadi satu skor komposit:

1. **Security** — aksi massa, kriminalitas, polemik sipil–militer
2. **Transport** — jalan tol, angkutan umum, bandara, pelabuhan, logistik
3. **Economy** — IHSG, nilai tukar, harga bahan bakar, kebijakan fiskal
4. **Cyber** — insiden siber pada sektor publik dan swasta
5. **Weather** — peringatan BMKG, banjir, cuaca ekstrem

## Komposit

Komposit dihitung sebagai rata-rata berbobot kelima pilar, dibulatkan ke bilangan bulat terdekat.

Bobot default pada `ingest/src/mjs_ingest/msrm.py`:

| Pilar | Bobot |
|---|---|
| Security | 0.30 |
| Transport | 0.25 |
| Economy | 0.20 |
| Cyber | 0.15 |
| Weather | 0.10 |

**Status bobot: provisional.** Dokumen doktrin MSRM v1.1 yang ada menetapkan skala dan daftar pilar, tetapi tidak menetapkan bobot komposit. Angka di atas adalah default yang dapat dikonfigurasi, bukan ketetapan doktrin. Bobot final menunggu konfirmasi penerbit; sampai itu terjadi setiap keluaran komposit harus dibaca sebagai hasil pembobotan konfigurasi, bukan hasil doktrin.

Aturan pengaman yang berlaku terlepas dari bobot: bila ada satu pilar berada pada band CRITICAL, komposit tidak boleh dilaporkan di bawah band HIGH. Rata-rata berbobot dapat meredam satu pilar ekstrem sampai menyesatkan, dan keselamatan manusia adalah prioritas pertama dalam urutan prioritas isu.

## Penandaan klaim

Setiap klaim dalam SITREP wajib bertanda `FACT`, `ANALYSIS`, atau `ASSUMPTION`. Tidak ada nilai default dan tidak ada klaim tanpa tanda.

- `FACT` — wajib memiliki sekurang-kurangnya satu rujukan sumber pada Source Reliability Table.
- `ANALYSIS` — penafsiran penyusun atas fakta yang sudah terdaftar.
- `ASSUMPTION` — premis yang belum terverifikasi, dinyatakan terbuka.

Bila data tidak tersedia, yang ditulis adalah "Data belum tersedia". Angka, nama, tanggal, kutipan, sumber, dan tautan tidak diestimasi dan tidak dikarang.

## Reliabilitas sumber

Tier yang dipakai: `A1`, `B2`, `B3`, `C3`. Setiap sumber dicatat pada Source Reliability Table dengan tier, penerbit, dan waktu pengambilan.

## Horizon

Rekomendasi tindakan memakai empat horizon: `0-6h`, `0-24h`, `0-72h`, `0-30d`.

Outlook prediktif dibatasi maksimum **H+2**. Proyeksi melampaui dua hari ditolak pada tahap validasi.
