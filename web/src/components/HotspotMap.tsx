import { BRAND } from "@/lib/bands";
import type { PointStat } from "@/types/sitrep";

import { TableScroll } from "./TableScroll";

/**
 * Sebaran titik awal aksi.
 *
 * Peta hanya menempatkan titik yang berkoordinat. Titik tanpa koordinat tidak
 * ditebak letaknya dan tidak dihilangkan: keduanya akan menyesatkan pembaca
 * yang memakai halaman ini untuk rencana lalu lintas. Titik seperti itu tetap
 * muncul pada peringkat di bawah peta.
 */
export function HotspotMap({ points }: { points: PointStat[] }) {
  const located = points.filter(
    (p) => p.located && p.lat !== null && p.lon !== null,
  );
  const top = points.slice(0, 20);

  return (
    <section aria-labelledby="sebaran" className="mt-10">
      <h2 id="sebaran" className="mb-1 text-lg font-bold text-[#0B1B3B]">
        Sebaran Titik Awal
      </h2>
      <p className="mb-3 text-sm text-[#3d4350]">
        {located.length} dari {points.length} titik memiliki koordinat.
      </p>

      {located.length > 0 ? (
        <PointPlot points={located} />
      ) : (
        <p className="mb-4 border-l-4 border-[#B8860B] bg-white px-3 py-2 text-sm text-[#3d4350]">
          Peta belum dapat ditampilkan karena gazetteer belum memuat koordinat.
          Koordinat diisi pada <code>data/gazetteer.json</code> beserta
          sumbernya; koordinat tanpa sumber tidak dicatat. Peringkat titik di
          bawah tetap berlaku tanpa koordinat.
        </p>
      )}

      <TableScroll>
        <table className="w-full min-w-[40rem] border-collapse text-sm">
          <thead>
            <tr style={{ backgroundColor: BRAND.navy }} className="text-white">
              <th className="w-10 px-3 py-2 text-right font-bold">#</th>
              <th className="px-3 py-2 font-bold">Titik</th>
              <th className="w-20 px-3 py-2 text-right font-bold">Aksi</th>
              <th className="w-20 px-3 py-2 text-right font-bold">Hari</th>
              <th className="w-28 px-3 py-2 text-right font-bold">Massa</th>
              <th className="w-28 px-3 py-2 font-bold">Koordinat</th>
            </tr>
          </thead>
          <tbody>
            {top.map((point, i) => (
              <tr
                key={point.key}
                className="border-b border-[#dfe3ea] bg-white"
              >
                <td className="px-3 py-2 text-right tabular-nums text-[#6b7280]">
                  {i + 1}
                </td>
                <td className="px-3 py-2 font-bold text-[#16181d]">
                  {point.label}
                </td>
                <td className="px-3 py-2 text-right tabular-nums text-[#16181d]">
                  {point.actions}
                </td>
                <td className="px-3 py-2 text-right tabular-nums text-[#3d4350]">
                  {new Set(point.dates).size}
                </td>
                <td className="px-3 py-2 text-right tabular-nums text-[#3d4350]">
                  {point.crowd_reported.toLocaleString("id-ID")}
                </td>
                <td className="px-3 py-2 text-[#3d4350]">
                  {point.located
                    ? `${point.lat?.toFixed(4)}, ${point.lon?.toFixed(4)}`
                    : "Data belum tersedia"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableScroll>
    </section>
  );
}

/**
 * Penempatan titik pada bidang lintang-bujur.
 *
 * Proyeksi disesuaikan dengan kotak pembatas data, bukan dengan satu skala
 * tetap, agar sebaran yang rapat tetap terbaca. Ukuran lingkaran mengikuti
 * akar jumlah aksi sehingga luasnya sebanding dengan jumlah, bukan jari-jarinya.
 */
function PointPlot({ points }: { points: PointStat[] }) {
  const lats = points.map((p) => p.lat as number);
  const lons = points.map((p) => p.lon as number);

  const pad = 0.01;
  const minLat = Math.min(...lats) - pad;
  const maxLat = Math.max(...lats) + pad;
  const minLon = Math.min(...lons) - pad;
  const maxLon = Math.max(...lons) + pad;

  const width = 960;
  const height = 540;
  const maxActions = Math.max(...points.map((p) => p.actions), 1);

  const x = (lon: number) => ((lon - minLon) / (maxLon - minLon)) * width;
  // Lintang naik ke utara, sumbu y layar naik ke bawah.
  const y = (lat: number) =>
    height - ((lat - minLat) / (maxLat - minLat)) * height;

  return (
    <figure className="mb-4 bg-white p-3">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="h-auto w-full"
        role="img"
        aria-label="Sebaran titik awal aksi menurut koordinat"
      >
        <rect width={width} height={height} fill="#f5f6f8" />
        {points.map((point) => {
          const cx = x(point.lon as number);
          const cy = y(point.lat as number);
          const r = 6 + Math.sqrt(point.actions / maxActions) * 22;
          return (
            <g key={point.key}>
              <circle
                cx={cx}
                cy={cy}
                r={r}
                fill={BRAND.navy}
                fillOpacity={0.22}
                stroke={BRAND.navy}
                strokeWidth={2}
              />
              <text
                x={cx}
                y={cy + 4}
                textAnchor="middle"
                fontSize={13}
                fontWeight="bold"
                fill={BRAND.navy}
              >
                {point.actions}
              </text>
              <text
                x={cx}
                y={cy + r + 14}
                textAnchor="middle"
                fontSize={11}
                fill="#3d4350"
              >
                {point.label}
              </text>
            </g>
          );
        })}
      </svg>
      <figcaption className="mt-2 text-xs text-[#6b7280]">
        Angka di dalam lingkaran adalah jumlah rencana aksi pada titik itu. Luas
        lingkaran sebanding dengan jumlah tersebut.
      </figcaption>
    </figure>
  );
}
