import { AlertTable } from "@/components/AlertTable";
import { ContactBlock } from "@/components/ContactBlock";
import { EditionHeader } from "@/components/EditionHeader";
import { RiskDashboard } from "@/components/RiskDashboard";
import { SectionList } from "@/components/SectionList";
import { SourceTable } from "@/components/SourceTable";
import { ZoneTable } from "@/components/ZoneTable";
import { readLatest } from "@/lib/sitrep";

/**
 * Halaman edisi terbaru.
 *
 * Dirender di server dan membaca arsip pada tiap permintaan, sehingga edisi
 * baru muncul tanpa build ulang.
 */
export const dynamic = "force-dynamic";

export default async function Page() {
  const { sitrep, isExample } = await readLatest();

  return (
    <main>
      <EditionHeader edition={sitrep.edition} isExample={isExample} />

      <div className="mx-auto max-w-6xl px-6 pb-4">
        <RiskDashboard risk={sitrep.risk} />
        <AlertTable alerts={sitrep.alerts} />
        <ZoneTable zones={sitrep.zones} />
        <SectionList sections={sitrep.sections} />
        <SourceTable sources={sitrep.sources} />
      </div>

      <ContactBlock classification={sitrep.edition.classification} />
    </main>
  );
}
