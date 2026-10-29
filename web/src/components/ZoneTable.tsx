import { BAND_FILL, BAND_INK, BAND_LABEL, BRAND, bandOf } from "@/lib/bands";
import type { Zone } from "@/types/sitrep";

/** Regional risk map Jabodetabek, disajikan sebagai tabel terurut. */
export function ZoneTable({ zones }: { zones: Zone[] }) {
  if (zones.length === 0) {
    return null;
  }

  const sorted = [...zones].sort((a, b) => b.score - a.score);

  return (
    <section aria-labelledby="zone-map" className="mt-10">
      <h2 id="zone-map" className="mb-3 text-lg font-bold text-[#0B1B3B]">
        Regional Risk Map — Jabodetabek
      </h2>

      <table className="w-full border-collapse text-sm">
        <thead>
          <tr style={{ backgroundColor: BRAND.navy }} className="text-white">
            <th className="px-3 py-2 font-bold">Zona</th>
            <th className="w-20 px-3 py-2 text-right font-bold">Skor</th>
            <th className="w-28 px-3 py-2 font-bold">Band</th>
            <th className="px-3 py-2 font-bold">Pemicu</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((zone) => {
            const band = bandOf(zone.score);
            return (
              <tr key={zone.zone} className="border-b border-[#dfe3ea] bg-white">
                <td className="px-3 py-2 font-bold text-[#16181d]">{zone.zone}</td>
                <td
                  className="px-3 py-2 text-right font-bold tabular-nums"
                  style={{ backgroundColor: BAND_FILL[band], color: BAND_INK[band] }}
                >
                  {zone.score}
                </td>
                <td
                  className="px-3 py-2 font-bold"
                  style={{ backgroundColor: BAND_FILL[band], color: BAND_INK[band] }}
                >
                  {BAND_LABEL[band]}
                </td>
                <td className="px-3 py-2 text-[#3d4350]">
                  {zone.drivers && zone.drivers.length > 0
                    ? zone.drivers.join("; ")
                    : "Data belum tersedia"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
