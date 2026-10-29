import type { Section } from "@/types/sitrep";

import { ClaimTagMark } from "./ClaimTagMark";

/**
 * Isi brief, satu blok per bagian.
 *
 * Setiap klaim dirender bersama tandanya. Klaim tanpa tanda tidak
 * disembunyikan dan tidak diberi tanda bawaan, melainkan ditampilkan apa
 * adanya dengan keterangan bahwa tandanya belum ada, agar kekurangan itu
 * terlihat pembaca dan bukan hanya terlihat validator.
 */
export function SectionList({ sections }: { sections: Section[] }) {
  return (
    <section aria-labelledby="brief-body" className="mt-10">
      <h2 id="brief-body" className="mb-3 text-lg font-bold text-[#0B1B3B]">
        Isi Brief
      </h2>

      <div className="space-y-5">
        {sections.map((section) => (
          <article
            key={section.key}
            className="border-l-4 border-[#B8860B] bg-white px-4 py-3"
          >
            <h3 className="mb-2 font-bold text-[#0B1B3B]">{section.title}</h3>
            <ul className="space-y-2">
              {section.claims.map((claim, i) => (
                <li key={i} className="text-sm leading-relaxed text-[#16181d]">
                  {claim.tag ? (
                    <ClaimTagMark tag={claim.tag} />
                  ) : (
                    <span className="mr-2 border border-dashed border-[#b91c1c] px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-[#b91c1c]">
                      tanpa tanda
                    </span>
                  )}
                  {claim.text}
                  {claim.source_ids && claim.source_ids.length > 0 ? (
                    <span className="ml-1 text-[#6b7280]">
                      [{claim.source_ids.join(", ")}]
                    </span>
                  ) : null}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}
