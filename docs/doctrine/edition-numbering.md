# Penomoran Edisi

Format identitas edisi: `MJS-YYYY-MM-DD-NNN`

- `YYYY-MM-DD` — tanggal terbit
- `NNN` — penghitung edisi, zero-pad tiga digit (`032`, bukan `32`)

Penghitung bersifat berurutan dan monoton: `NNN` edisi baru adalah `NNN` terakhir pada arsip ditambah satu. Penghitung tidak direset per tanggal atau per bulan.

Nama berkas yang dihasilkan jalur produksi:

| Produk | Pola nama |
|---|---|
| Brief utama (DOCX, English) | `MJS-YYYY-MM-DD-NNN-PREVIEW-EN.docx` |
| Versi WhatsApp (TXT, Indonesia) | `MJS-YYYY-MM-DD-NNN-WA-ID.txt` |

Dashboard membaca penomoran ini sebagai kunci urut utama. Dua edisi dengan `NNN` sama dianggap konflik arsip dan ditandai, tidak digabung secara diam-diam.
