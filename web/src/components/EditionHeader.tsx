import { BRAND, CLASSIFICATION_LABEL } from "@/lib/bands";
import type { Edition } from "@/types/sitrep";

export function EditionHeader({ edition, isExample }: { edition: Edition; isExample: boolean }) {
  return (
    <header style={{ backgroundColor: BRAND.navy }} className="text-white">
      <div className="mx-auto max-w-6xl px-6 py-5">
        <div
          className="mb-3 border-b pb-3 text-[11px] font-bold uppercase tracking-[0.18em]"
          style={{ borderColor: BRAND.gold, color: BRAND.gold }}
        >
          {CLASSIFICATION_LABEL[edition.classification]}
        </div>

        <h1 className="text-2xl font-bold">MJ-Sentinel Strategic Intelligence SITREP</h1>

        <dl className="mt-3 flex flex-wrap gap-x-8 gap-y-1 text-sm text-[#c9cfdb]">
          <div>
            <dt className="inline font-bold text-white">Edisi: </dt>
            <dd className="inline tabular-nums">{edition.id}</dd>
          </div>
          <div>
            <dt className="inline font-bold text-white">Tier: </dt>
            <dd className="inline">{edition.tier}</dd>
          </div>
          <div>
            <dt className="inline font-bold text-white">Theatre: </dt>
            <dd className="inline">{edition.theatre_primary ?? "JABODETABEK"}</dd>
          </div>
          <div>
            <dt className="inline font-bold text-white">Metodologi: </dt>
            <dd className="inline">{edition.methodology}</dd>
          </div>
          {edition.cutoff ? (
            <div>
              <dt className="inline font-bold text-white">Cut-off: </dt>
              <dd className="inline tabular-nums">{edition.cutoff}</dd>
            </div>
          ) : null}
        </dl>

        {isExample ? (
          <p
            className="mt-4 border-l-4 bg-[#132548] px-3 py-2 text-sm"
            style={{ borderLeftColor: BRAND.gold }}
          >
            Arsip masih kosong. Yang ditampilkan adalah contoh bentuk data dari
            <code className="mx-1 bg-[#0b1b3b] px-1">schema/example.sitrep.json</code>, bukan
            penilaian risiko. Seluruh skor bernilai nol karena data belum tersedia.
          </p>
        ) : null}
      </div>
    </header>
  );
}
