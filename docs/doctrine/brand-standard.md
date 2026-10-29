# Brand Standard — MJ-Sentinel

Berlaku untuk dokumen terbit (DOCX) dan untuk antarmuka dashboard.

## Warna

| Token | Nilai | Pemakaian |
|---|---|---|
| Navy | `#0B1B3B` | Latar cover, header tabel, blok kontak |
| Gold | `#B8860B` | Aksen, garis pemisah, penanda edisi |

Latar cover adalah navy, bukan hitam.

## Band risiko

Sel tabel dan penanda zona memakai isian lembut:

| Band | Isian |
|---|---|
| LOW | hijau muda |
| MODERATE | kuning muda |
| HIGH | oranye muda |
| CRITICAL | merah muda |

Nilai heksadesimal tunggal untuk kedua medium didefinisikan di `web/src/lib/bands.ts` dan `ingest/src/mjs_ingest/msrm.py`, agar DOCX dan dashboard tidak menyimpang.

## Tipografi

Dokumen terbit memakai Arial. Heading bold navy, body 10–11pt. Dashboard memakai tumpukan sans-serif sistem yang menempatkan Arial lebih dahulu, sehingga tampilan layar tidak menjauh dari dokumen cetak.

## Larangan

- Emoji dan ikon dekoratif.
- Elemen yang berkesan kekanakan atau berkesan dihasilkan mesin.
- Superlatif atas gagasan internal tanpa dasar empiris.
- Penyebutan nama firma intelijen atau konsultan asing pada produk apa pun.

## Blok kontak

Wajib pada akhir dokumen terbit, shading navy dengan teks putih:

```
Matajaga Research — Strategic Risk & Intelligence Unit
PT HRM Multi Sinergy  |  Direktur: Toni Hendrawan
Email: research@matajaga.id  |  Operations: ops@matajaga.id
Editorial revisions / errata: editorial@matajaga.id
```

## Catatan palet — hasil pemeriksaan

Isian band diperiksa dengan validator palet (OKLab, Delta E, simulasi defisiensi penglihatan warna, kontras terhadap latar). Hasilnya dicatat di sini agar batasnya diketahui, bukan ditemukan ulang setiap kali:

| Pemeriksaan | Hasil |
|---|---|
| Kontras isian terhadap latar | di bawah 3:1 pada keempat band |
| Pemisahan HIGH dan CRITICAL (penglihatan normal) | ΔE 4.2 |
| Pemisahan LOW dan MODERATE (protanopia) | ΔE 2.4 |

Angka itu jauh di bawah ambang yang dapat dibedakan dengan percaya diri. Konsekuensinya mengikat: **warna tidak boleh menjadi satu-satunya pembawa band**. Setiap penanda band, pada dokumen maupun pada layar, wajib menuliskan skor dan nama band sebagai teks. Dua band yang paling sulit dibedakan secara visual, HIGH dan CRITICAL, justru dua band yang paling menentukan keputusan operasional.

Jalur perbaikan yang lazim — menambah ikon status atau tekstur — tertutup oleh larangan ikon dekoratif di atas. Karena itu teks yang menanggung seluruh beban pembedaan.

Isian pada tabel band dipertahankan apa adanya karena ditetapkan brand standard. Bila penerbit kelak meninjau palet, keempat isian itulah yang perlu dilangkahkan lebih jauh satu sama lain.
