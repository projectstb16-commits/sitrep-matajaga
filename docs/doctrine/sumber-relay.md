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

## Rencana dan kejadian

Rekap menyatakan apa yang direncanakan. Pesan susulan melaporkan apa yang terpantau: massa tiba, massa membubarkan diri, akses ditutup atau dibuka, situasi dinyatakan aman. Keduanya dipetakan berdasarkan kesamaan tanggal dan titik.

Batas yang mengikat: **tidak adanya laporan lapangan bukan bukti tidak terjadinya kegiatan.**

Grup relay melaporkan sebagian kecil kegiatan saja. Pada satu berkas uji, 287 rencana hanya disertai 60 laporan keadaan, dan hanya 4 rencana memiliki laporan yang menyebut titiknya. Angka itu menunjukkan kepadatan pelaporan, bukan tingkat pelaksanaan.

Istilah "tingkat realisasi" karena itu tidak dipakai, dan bidang keluaran dinamai `plans_with_field_report` serta `plans_without_field_report`. Menyebutnya "terlaksana" dan "batal" akan mengubah ketiadaan pengamatan menjadi temuan, dan pembaca akan menyimpulkan 283 aksi tidak terjadi padahal yang benar adalah tidak ada yang melaporkannya.

## Koordinat dan gazetteer

Peta sebaran titik hanya menempatkan titik yang berkoordinat. Koordinat disimpan pada `data/gazetteer.json` bersama `source` yang menyebut asalnya dan `verified_at`.

Aturannya: **koordinat tanpa sumber tidak dicatat.** Koordinat yang ditulis dari ingatan terlihat persis seperti koordinat yang benar, dan pembaca yang memakai halaman ini untuk rencana lalu lintas akan diarahkan ke tempat yang salah. Entri tanpa koordinat tetap muncul pada peringkat titik rawan; yang tidak dapat dilakukan tanpa koordinat hanyalah penempatan pada peta.

Penambahan titik baru ke gazetteer tidak pernah menimpa koordinat yang sudah diisi.

## Jenis kegiatan pada format bernomor

Judul pesan berlaku untuk rekap wilayahnya, bukan untuk setiap baris di dalamnya. Butir yang tidak berada di bawah judul kecamatan dan tidak membawa tuntutan tidak dinyatakan unjuk rasa walau judul pesan menyebut unras.

Kalimat pembuka dan penutup laporan — "Demikian dilaporkan", "Izin melaporkan", "Terima kasih" — disaring sebelum baris dibaca sebagai nama pelaksana. Tanpa penyaringan itu, satu laporan uji melahirkan aksi berisi 1.200 orang dengan pelaksana "Demikian dilaporkan".
