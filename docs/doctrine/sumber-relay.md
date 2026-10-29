# Sumber Relay dan Data Pribadi

## Apa itu rekap relay

Grup pesan meneruskan rekap "rengiat" — rencana kegiatan unjuk rasa dan kegiatan masyarakat — berisi jam, lokasi, organisasi pelaksana, penanggung jawab, perkiraan jumlah massa, dan tuntutan. Rekap ini beredar luas dan tidak diterbitkan secara resmi kepada penerbit.

## Tier reliabilitas

Rekap relay dicatat sebagai **C3** pada Source Reliability Table, tanpa kecuali.

Dasarnya: penerbit menerima rekap sebagai teruskan, bukan dari instansi penerbitnya. Rantai penerusan tidak dapat ditelusuri, dan isinya tidak dikonfirmasi. Rekap boleh jadi berasal dari dokumen resmi, tetapi yang dapat dipastikan penerbit hanyalah bahwa rekap itu diterima — bukan bahwa isinya benar.

Menaikkan tier karena rekap "terlihat resmi" akan membuat pembaca memperlakukan teruskan sebagai keterangan instansi.

## Bentuk klaim

Klaim yang diturunkan dari rekap relay dirumuskan sebagai laporan, bukan sebagai kepastian:

> Relay melaporkan rencana unjuk rasa pada 2026-10-23 pukul 13.00 WIB di [lokasi] oleh [organisasi]. Jumlah massa yang dilaporkan 20 orang.

Yang dapat dipastikan adalah adanya laporan, bukan terjadinya kegiatan. Rencana dapat berubah, dibatalkan, atau tidak pernah dimaksudkan terjadi. Rumusan di atas menjaga perbedaan itu tetap terlihat saat dibaca sepintas.

## Jumlah massa bukan skor

Jumlah massa yang tercantum adalah angka yang dilaporkan relay. Angka itu tidak diubah menjadi skor pilar Security secara otomatis.

Penilaian risiko adalah pekerjaan analis. Rumus yang menurunkan skor dari jumlah massa akan menghasilkan angka yang tidak berasal dari siapa pun, namun terbaca sebagai hasil MSRM.

## Jenis kegiatan tidak ditebak

Rekap memuat konser, lomba lari, dan wisuda bersama unjuk rasa, kerap di bawah satu judul yang sama. Jenis ditentukan dari bukti pada butir itu sendiri: bidang "Bentuk giat" bila ada, lalu keberadaan "Tuntutan". Butir tanpa keduanya dicatat sebagai `tidak_ditentukan`.

Alasannya terukur. Pada satu berkas uji, menetapkan jenis dari judul seksi menghasilkan 313.639 orang terhitung sebagai massa unjuk rasa; setelah jenis ditentukan dari bukti per butir, angkanya 11.775. Selisihnya adalah penonton konser dan peserta lomba lari.

## Data pribadi

Rekap memuat nama penanggung jawab aksi dan nomor telepon pelapor. Keduanya milik orang yang dapat diidentifikasi, dan sebagian adalah penyelenggara aksi terhadap pemerintah maupun perusahaan.

Aturan yang berlaku:

1. **Nomor telepon tidak pernah disimpan.** Nomor dihapus dari setiap nilai bidang pada tahap pembersihan, termasuk ketika penyertaan nama dipilih.
2. **Nama penanggung jawab disunting secara bawaan.** Penyertaannya memerlukan `--include-pii`, dan keluaran itu membawa peringatan.
3. **Keluaran yang memuat nama tidak boleh masuk repositori atau saluran terbuka.** Repositori ini publik; seluruh isi `data/sitreps/` karena itu tidak masuk version control.

Daftar nama penyelenggara aksi beserta jadwalnya, bila tersebar, membahayakan orang per orang. Penyuntingan bawaan menjadikan penyertaan nama sebagai keputusan sadar, bukan keadaan yang terjadi karena tidak ada yang memikirkannya.
