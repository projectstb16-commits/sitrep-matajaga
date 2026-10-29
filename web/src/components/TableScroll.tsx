/**
 * Pembungkus tabel yang dapat digulir mendatar.
 *
 * Tabel rekap membawa lima kolom dan tidak dapat diringkas tanpa membuang
 * keterangan. Di lebar ponsel, tanpa pembungkus ini seluruh halaman ikut
 * tergeser dan kolom pertama hilang dari pandangan.
 */
export function TableScroll({ children }: { children: React.ReactNode }) {
  return <div className="overflow-x-auto">{children}</div>;
}
