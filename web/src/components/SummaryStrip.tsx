import type { Analysis } from "@/types/sitrep";

/**
 * Angka pokok di kepala halaman.
 *
 * Disajikan sebagai angka, bukan grafik: satu nilai tunggal tidak memperoleh
 * apa pun dari sumbu atau batang. Tidak ada band warna di sini, karena angka
 * ini hitungan laporan dan bukan penilaian risiko.
 */
export function SummaryStrip({ analysis }: { analysis: Analysis }) {
  const { points, field_reports, totals, counts, window } = analysis;

  const tiles = [
    {
      label: "Rencana aksi",
      value: totals.plans_analysed.toLocaleString("id-ID"),
    },
    {
      label: "Titik aksi",
      value: points.coverage.points.toLocaleString("id-ID"),
    },
    {
      label: "Penumpukan titik",
      value: analysis.patterns.concurrency.length.toLocaleString("id-ID"),
    },
    {
      label: "Laporan lapangan",
      value: field_reports.reports.length.toLocaleString("id-ID"),
    },
    {
      label: "Laporan ulang disatukan",
      value: counts.duplicates_merged.toLocaleString("id-ID"),
    },
  ];

  return (
    <section aria-labelledby="ringkasan" className="mt-8">
      <h2 id="ringkasan" className="mb-1 text-lg font-bold text-[#0B1B3B]">
        Ringkasan
      </h2>
      <p className="mb-3 text-sm text-[#3d4350]">
        Jendela data {window.from} sampai {window.to}, dari {totals.messages}{" "}
        pesan relay. Seluruh angka pada halaman ini adalah hitungan atas
        laporan, bukan penilaian risiko.
      </p>

      <dl className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {tiles.map((tile) => (
          <div
            key={tile.label}
            className="border-l-4 border-[#0B1B3B] bg-white px-3 py-2"
          >
            <dt className="text-[11px] font-bold uppercase tracking-wide text-[#3d4350]">
              {tile.label}
            </dt>
            <dd className="text-2xl font-bold tabular-nums text-[#0B1B3B]">
              {tile.value}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
