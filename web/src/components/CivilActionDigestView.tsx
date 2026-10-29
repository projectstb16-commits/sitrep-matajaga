import { TableScroll } from "./TableScroll";

import { BRAND } from "@/lib/bands";
import type { CivilAction, CivilActionDigest } from "@/types/sitrep";

const KIND_LABEL: Record<CivilAction["kind"], string> = {
  unjuk_rasa: "Unjuk rasa",
  giat_masyarakat: "Giat masyarakat",
  giat_kepolisian: "Giat kepolisian",
  tidak_ditentukan: "Tidak ditentukan",
};

/**
 * Rekap kegiatan sipil hasil ekstraksi relay.
 *
 * Bagian ini tidak menampilkan band risiko, dan itu disengaja. Rekap adalah
 * kumpulan laporan, bukan penilaian; memberinya warna band akan membuatnya
 * terbaca sebagai hasil penilaian yang tidak pernah dibuat siapa pun.
 */
export function CivilActionDigestView({
  digest,
}: {
  digest: CivilActionDigest;
}) {
  const upcoming = [...digest.actions].sort((a, b) =>
    `${a.activity_date ?? ""}${a.time_start ?? ""}`.localeCompare(
      `${b.activity_date ?? ""}${b.time_start ?? ""}`,
    ),
  );

  const demonstrations = upcoming.filter((a) => a.kind === "unjuk_rasa");
  const kinds = Object.entries(digest.counts.by_kind).sort(
    (a, b) => b[1].actions - a[1].actions,
  );

  return (
    <section aria-labelledby="civil-action" className="mt-10">
      <h2 id="civil-action" className="mb-1 text-lg font-bold text-[#0B1B3B]">
        Civil Action Watch
      </h2>
      <p className="mb-3 text-sm text-[#3d4350]">
        {digest.window.from} sampai {digest.window.to}. Sumber:{" "}
        {digest.source.publisher} (tier {digest.source.reliability}). Angka
        jumlah massa adalah yang dilaporkan relay, bukan penilaian penerbit.
        {digest.redacted
          ? " Nama penanggung jawab tidak disertakan."
          : " Keluaran ini memuat nama penanggung jawab."}
      </p>

      <TableScroll>
        <table className="mb-6 w-full min-w-[44rem] border-collapse text-sm">
          <caption className="sr-only">Hitungan kegiatan per jenis</caption>
          <thead>
            <tr style={{ backgroundColor: BRAND.navy }} className="text-white">
              <th className="px-3 py-2 font-bold">Jenis kegiatan</th>
              <th className="w-28 px-3 py-2 text-right font-bold">Kegiatan</th>
              <th className="w-40 px-3 py-2 text-right font-bold">
                Massa dilaporkan
              </th>
            </tr>
          </thead>
          <tbody>
            {kinds.map(([kind, count]) => (
              <tr key={kind} className="border-b border-[#dfe3ea] bg-white">
                <td className="px-3 py-2 text-[#16181d]">
                  {KIND_LABEL[kind as CivilAction["kind"]] ?? kind}
                </td>
                <td className="px-3 py-2 text-right tabular-nums text-[#16181d]">
                  {count.actions}
                </td>
                <td className="px-3 py-2 text-right tabular-nums text-[#16181d]">
                  {count.crowd_reported.toLocaleString("id-ID")}
                </td>
              </tr>
            ))}
            <tr className="border-b-2 border-[#0B1B3B] bg-[#eef0f4]">
              <td className="px-3 py-2 font-bold text-[#16181d]">
                Total kegiatan unik
              </td>
              <td className="px-3 py-2 text-right font-bold tabular-nums text-[#16181d]">
                {digest.counts.actions}
              </td>
              <td className="px-3 py-2 text-right text-[#3d4350]">
                {digest.counts.duplicates_merged} laporan ulang disatukan
              </td>
            </tr>
          </tbody>
        </table>
      </TableScroll>

      <h3 className="mb-2 font-bold text-[#0B1B3B]">
        Rencana unjuk rasa terlapor ({demonstrations.length})
      </h3>

      <TableScroll>
        <table className="w-full min-w-[44rem] border-collapse text-sm">
          <thead>
            <tr style={{ backgroundColor: BRAND.navy }} className="text-white">
              <th className="w-28 px-3 py-2 font-bold">Tanggal</th>
              <th className="w-20 px-3 py-2 font-bold">Jam</th>
              <th className="w-24 px-3 py-2 font-bold">Zona</th>
              <th className="px-3 py-2 font-bold">Lokasi dan pelaksana</th>
              <th className="w-24 px-3 py-2 text-right font-bold">Massa</th>
            </tr>
          </thead>
          <tbody>
            {demonstrations.map((action, i) => (
              <tr
                key={i}
                className="border-b border-[#dfe3ea] bg-white align-top"
              >
                <td className="px-3 py-2 tabular-nums text-[#16181d]">
                  {action.activity_date ?? "Data belum tersedia"}
                </td>
                <td className="px-3 py-2 tabular-nums text-[#16181d]">
                  {action.time_start ?? "—"}
                </td>
                <td className="px-3 py-2 font-bold text-[#16181d]">
                  {action.region ?? "—"}
                </td>
                <td className="px-3 py-2 text-[#16181d]">
                  {action.location ?? "Data belum tersedia"}
                  {action.organizer ? (
                    <span className="block text-[#3d4350]">
                      {action.organizer}
                    </span>
                  ) : null}
                  {action.demand ? (
                    <span className="mt-1 block border-l-2 border-[#B8860B] pl-2 text-[#3d4350]">
                      {action.demand}
                    </span>
                  ) : null}
                </td>
                <td className="px-3 py-2 text-right tabular-nums text-[#16181d]">
                  {action.crowd_reported === null
                    ? "Data belum tersedia"
                    : action.crowd_reported.toLocaleString("id-ID")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableScroll>
    </section>
  );
}
