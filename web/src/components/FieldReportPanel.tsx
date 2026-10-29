import { BRAND } from "@/lib/bands";
import type { Analysis } from "@/types/sitrep";

import { TableScroll } from "./TableScroll";

const SIGNAL_LABEL: Record<string, string> = {
  massa_tiba: "Massa tiba",
  massa_bertahan: "Massa bertahan",
  massa_bubar: "Massa bubar",
  situasi_aman: "Situasi aman",
  lalin_macet: "Lalu lintas tersendat",
  akses_ditutup: "Akses ditutup",
  akses_dibuka: "Akses dibuka",
  nihil: "Nihil",
};

/**
 * Laporan keadaan lapangan dan pemetaannya terhadap rencana.
 *
 * Yang dihitung adalah berapa rencana yang memiliki laporan lapangan menyebut
 * titiknya. Sisanya tidak disebut batal: grup relay melaporkan sebagian kecil
 * kegiatan saja, dan ketiadaan laporan bukan bukti ketiadaan kegiatan.
 */
export function FieldReportPanel({ analysis }: { analysis: Analysis }) {
  const { observation, reports } = analysis.field_reports;
  const withTraffic = reports.filter((r) =>
    r.signals.some(
      (s) =>
        s === "lalin_macet" || s === "akses_ditutup" || s === "akses_dibuka",
    ),
  );

  return (
    <section aria-labelledby="lapangan" className="mt-10">
      <h2 id="lapangan" className="mb-1 text-lg font-bold text-[#0B1B3B]">
        Laporan Lapangan
      </h2>
      <p className="mb-3 text-sm text-[#3d4350]">
        {reports.length} laporan keadaan terdeteksi, {withTraffic.length} di
        antaranya menyebut dampak lalu lintas.{" "}
        {observation.plans_with_field_report} dari {observation.plans} rencana
        memiliki laporan lapangan yang menyebut titiknya.
      </p>

      <p className="mb-4 border-l-4 border-[#B8860B] bg-white px-3 py-2 text-sm text-[#3d4350]">
        {observation.note} Angka di atas karena itu tidak boleh dibaca sebagai
        tingkat realisasi, dan {observation.plans_without_field_report} rencana
        tanpa laporan tidak berarti batal.
      </p>

      <TableScroll>
        <table className="w-full min-w-[44rem] border-collapse text-sm">
          <thead>
            <tr style={{ backgroundColor: BRAND.navy }} className="text-white">
              <th className="w-28 px-3 py-2 font-bold">Tanggal</th>
              <th className="w-20 px-3 py-2 font-bold">Jam</th>
              <th className="w-56 px-3 py-2 font-bold">Keadaan terlapor</th>
              <th className="px-3 py-2 font-bold">Titik dan ruas disebut</th>
            </tr>
          </thead>
          <tbody>
            {reports.slice(0, 20).map((report, i) => (
              <tr
                key={i}
                className="border-b border-[#dfe3ea] bg-white align-top"
              >
                <td className="px-3 py-2 tabular-nums text-[#16181d]">
                  {report.reported_on}
                </td>
                <td className="px-3 py-2 tabular-nums text-[#16181d]">
                  {report.reported_time ?? "—"}
                </td>
                <td className="px-3 py-2 text-[#16181d]">
                  {report.signals.map((s) => SIGNAL_LABEL[s] ?? s).join(", ")}
                </td>
                <td className="px-3 py-2 text-[#3d4350]">
                  {report.point_keys.length > 0
                    ? report.point_keys.join("; ")
                    : "Titik tidak dikenali dari narasi"}
                  {report.roads.length > 0 ? (
                    <span className="mt-1 block border-l-2 border-[#B8860B] pl-2">
                      Ruas: {report.roads.join("; ")}
                    </span>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableScroll>
    </section>
  );
}
