import { BRAND } from "@/lib/bands";
import type { ConcurrencyRow } from "@/types/sitrep";

import { TableScroll } from "./TableScroll";

/**
 * Penumpukan beberapa kelompok pada satu titik dan jam yang sama.
 *
 * Bagian ini yang paling langsung terpakai untuk rencana lalu lintas. Enam
 * kelompok pada satu titik pukul 13.00 bukan enam peristiwa kecil yang
 * terpisah, dan daftar aksi per baris tidak memperlihatkan hal itu.
 */
export function ConcurrencyTable({ rows }: { rows: ConcurrencyRow[] }) {
  if (rows.length === 0) {
    return null;
  }

  return (
    <section aria-labelledby="penumpukan" className="mt-10">
      <h2 id="penumpukan" className="mb-1 text-lg font-bold text-[#0B1B3B]">
        Penumpukan Titik dan Jam ({rows.length})
      </h2>
      <p className="mb-3 text-sm text-[#3d4350]">
        Titik yang pada tanggal dan jam yang sama didatangi lebih dari satu
        kelompok, diurutkan dari penumpukan terbanyak.
      </p>

      <TableScroll>
        <table className="w-full min-w-[44rem] border-collapse text-sm">
          <thead>
            <tr style={{ backgroundColor: BRAND.navy }} className="text-white">
              <th className="w-28 px-3 py-2 font-bold">Tanggal</th>
              <th className="w-20 px-3 py-2 font-bold">Jam</th>
              <th className="px-3 py-2 font-bold">Titik</th>
              <th className="w-24 px-3 py-2 text-right font-bold">Kelompok</th>
              <th className="w-24 px-3 py-2 text-right font-bold">Massa</th>
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 15).map((row, i) => (
              <tr
                key={`${row.activity_date}-${row.time_start}-${row.point_key}-${i}`}
                className="border-b border-[#dfe3ea] bg-white align-top"
              >
                <td className="px-3 py-2 tabular-nums text-[#16181d]">
                  {row.activity_date}
                </td>
                <td className="px-3 py-2 tabular-nums text-[#16181d]">
                  {row.time_start}
                </td>
                <td className="px-3 py-2">
                  <span className="font-bold text-[#16181d]">{row.label}</span>
                  <span className="block text-xs text-[#6b7280]">
                    {row.organizers.join("; ")}
                  </span>
                </td>
                <td className="px-3 py-2 text-right font-bold tabular-nums text-[#16181d]">
                  {row.groups}
                </td>
                <td className="px-3 py-2 text-right tabular-nums text-[#3d4350]">
                  {row.crowd_reported.toLocaleString("id-ID")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableScroll>
    </section>
  );
}
