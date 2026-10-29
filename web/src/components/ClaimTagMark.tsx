import type { ClaimTag } from "@/types/sitrep";

/**
 * Penanda FACT / ANALYSIS / ASSUMPTION.
 *
 * Tanda ditulis sebagai teks, bukan sebagai ikon atau warna semata, karena
 * pembaca harus dapat membedakan fakta dari penafsiran tanpa bergantung pada
 * persepsi warna.
 */
const STYLE: Record<ClaimTag, string> = {
  FACT: "border-[#0B1B3B] text-[#0B1B3B]",
  ANALYSIS: "border-[#B8860B] text-[#7a5a07]",
  ASSUMPTION: "border-[#6b7280] text-[#4b5563]",
};

export function ClaimTagMark({ tag }: { tag: ClaimTag }) {
  return (
    <span
      className={`mr-2 shrink-0 border px-1.5 py-0.5 align-middle text-[10px] font-bold uppercase tracking-wider ${STYLE[tag]}`}
    >
      {tag}
    </span>
  );
}
