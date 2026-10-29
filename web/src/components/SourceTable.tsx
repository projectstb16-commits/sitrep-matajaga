import { BRAND } from "@/lib/bands";
import type { Source } from "@/types/sitrep";

/** Source Reliability Table. */
export function SourceTable({ sources }: { sources: Source[] }) {
  if (sources.length === 0) {
    return (
      <section aria-labelledby="sources" className="mt-10">
        <h2 id="sources" className="mb-3 text-lg font-bold text-[#0B1B3B]">
          Source Reliability Table
        </h2>
        <p className="border-l-4 border-[#dfe3ea] bg-white px-3 py-2 text-sm text-[#3d4350]">
          Data belum tersedia.
        </p>
      </section>
    );
  }

  return (
    <section aria-labelledby="sources" className="mt-10">
      <h2 id="sources" className="mb-3 text-lg font-bold text-[#0B1B3B]">
        Source Reliability Table
      </h2>

      <table className="w-full border-collapse text-sm">
        <thead>
          <tr style={{ backgroundColor: BRAND.navy }} className="text-white">
            <th className="w-16 px-3 py-2 font-bold">ID</th>
            <th className="w-16 px-3 py-2 font-bold">Tier</th>
            <th className="px-3 py-2 font-bold">Penerbit</th>
            <th className="px-3 py-2 font-bold">Judul</th>
          </tr>
        </thead>
        <tbody>
          {sources.map((source) => (
            <tr key={source.id} className="border-b border-[#dfe3ea] bg-white">
              <td className="px-3 py-2 font-bold tabular-nums text-[#16181d]">{source.id}</td>
              <td className="px-3 py-2 font-bold tabular-nums text-[#16181d]">
                {source.reliability}
              </td>
              <td className="px-3 py-2 text-[#16181d]">{source.publisher}</td>
              <td className="px-3 py-2 text-[#3d4350]">
                {source.url ? (
                  <a
                    href={source.url}
                    className="underline decoration-[#B8860B] underline-offset-2"
                    rel="noreferrer noopener"
                    target="_blank"
                  >
                    {source.title ?? source.url}
                  </a>
                ) : (
                  (source.title ?? "Data belum tersedia")
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
