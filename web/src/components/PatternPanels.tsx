import type { Analysis } from "@/types/sitrep";

import { BarRow } from "./BarRow";
import { TableScroll } from "./TableScroll";
import { BRAND } from "@/lib/bands";

/**
 * Pola berulang pada rekap rencana.
 *
 * Panel ini menampilkan hitungan masa lalu. Tidak ada proyeksi ke hari
 * berikutnya: perkiraan adalah pekerjaan analis dan tunduk pada batas
 * outlook H+2.
 */
export function PatternPanels({ analysis }: { analysis: Analysis }) {
  const { by_date, by_hour, by_weekday, recurring_organizers } =
    analysis.patterns;

  const maxHour = Math.max(...by_hour.map((r) => r.actions), 0);
  const maxDate = Math.max(...by_date.map((r) => r.actions), 0);

  return (
    <section aria-labelledby="pola" className="mt-10">
      <h2 id="pola" className="mb-3 text-lg font-bold text-[#0B1B3B]">
        Pola Berulang
      </h2>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="bg-white px-4 py-3">
          <h3 className="mb-2 font-bold text-[#0B1B3B]">Jam mulai aksi</h3>
          <p className="mb-2 text-sm text-[#3d4350]">
            Jumlah rencana aksi menurut jam mulai. Dua puncak menentukan jendela
            pengaturan lalu lintas.
          </p>
          {by_hour.map((row) => (
            <BarRow
              key={row.hour}
              label={`${String(row.hour).padStart(2, "0")}.00 WIB`}
              value={row.actions}
              max={maxHour}
            />
          ))}
        </div>

        <div className="bg-white px-4 py-3">
          <h3 className="mb-2 font-bold text-[#0B1B3B]">
            Rencana aksi per tanggal
          </h3>
          <p className="mb-2 text-sm text-[#3d4350]">
            Jumlah rencana per hari terbit, beserta nama harinya.
          </p>
          {by_date.map((row) => (
            <BarRow
              key={row.date}
              label={row.date}
              value={row.actions}
              max={maxDate}
              caption={row.weekday ?? undefined}
            />
          ))}
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div>
          <h3 className="mb-2 font-bold text-[#0B1B3B]">
            Sebaran hari dalam pekan
          </h3>
          <TableScroll>
            <table className="w-full min-w-[22rem] border-collapse text-sm">
              <thead>
                <tr
                  style={{ backgroundColor: BRAND.navy }}
                  className="text-white"
                >
                  <th className="px-3 py-2 font-bold">Hari</th>
                  <th className="w-24 px-3 py-2 text-right font-bold">Aksi</th>
                  <th className="w-32 px-3 py-2 text-right font-bold">
                    Hari teramati
                  </th>
                </tr>
              </thead>
              <tbody>
                {by_weekday.map((row) => (
                  <tr
                    key={row.weekday}
                    className="border-b border-[#dfe3ea] bg-white"
                  >
                    <td className="px-3 py-2 text-[#16181d]">{row.weekday}</td>
                    <td className="px-3 py-2 text-right tabular-nums text-[#16181d]">
                      {row.actions}
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums text-[#3d4350]">
                      {row.days_observed}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TableScroll>
          <p className="mt-2 text-xs text-[#6b7280]">
            Kolom hari teramati menunjukkan dasar hitungan. Jendela data sepuluh
            hari terlalu pendek untuk dibaca sebagai kecenderungan mingguan.
          </p>
        </div>

        <div>
          <h3 className="mb-2 font-bold text-[#0B1B3B]">
            Pelaksana berulang ({recurring_organizers.length})
          </h3>
          <TableScroll>
            <table className="w-full min-w-[22rem] border-collapse text-sm">
              <thead>
                <tr
                  style={{ backgroundColor: BRAND.navy }}
                  className="text-white"
                >
                  <th className="px-3 py-2 font-bold">Pelaksana</th>
                  <th className="w-20 px-3 py-2 text-right font-bold">Hari</th>
                  <th className="w-20 px-3 py-2 text-right font-bold">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {recurring_organizers.slice(0, 10).map((row) => (
                  <tr
                    key={row.organizer}
                    className="border-b border-[#dfe3ea] bg-white"
                  >
                    <td className="px-3 py-2 text-[#16181d]">
                      {row.organizer}
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums text-[#16181d]">
                      {row.days}
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums text-[#3d4350]">
                      {row.actions}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TableScroll>
        </div>
      </div>
    </section>
  );
}
