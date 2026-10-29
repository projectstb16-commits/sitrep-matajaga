import { AlertTable } from "@/components/AlertTable";
import { CivilActionDigestView } from "@/components/CivilActionDigestView";
import { ConcurrencyTable } from "@/components/ConcurrencyTable";
import { FieldReportPanel } from "@/components/FieldReportPanel";
import { HotspotMap } from "@/components/HotspotMap";
import { PatternPanels } from "@/components/PatternPanels";
import { SummaryStrip } from "@/components/SummaryStrip";
import { ContactBlock } from "@/components/ContactBlock";
import { EditionHeader } from "@/components/EditionHeader";
import { RiskDashboard } from "@/components/RiskDashboard";
import { SectionList } from "@/components/SectionList";
import { SourceTable } from "@/components/SourceTable";
import { ZoneTable } from "@/components/ZoneTable";
import { readAnalysis, readDigest, readLatest } from "@/lib/sitrep";

/**
 * Halaman edisi terbaru.
 *
 * Dirender di server dan membaca arsip pada tiap permintaan, sehingga edisi
 * baru muncul tanpa build ulang.
 */
export const dynamic = "force-dynamic";

export default async function Page() {
  const [{ sitrep, isExample }, digest, analysis] = await Promise.all([
    readLatest(),
    readDigest(),
    readAnalysis(),
  ]);

  return (
    <main>
      <EditionHeader edition={sitrep.edition} isExample={isExample} />

      <div className="mx-auto max-w-6xl px-6 pb-4">
        {analysis ? <SummaryStrip analysis={analysis} /> : null}
        <RiskDashboard risk={sitrep.risk} />
        <AlertTable alerts={sitrep.alerts} />
        {analysis ? <HotspotMap points={analysis.points.ranked} /> : null}
        {analysis ? (
          <ConcurrencyTable rows={analysis.patterns.concurrency} />
        ) : null}
        {analysis ? <PatternPanels analysis={analysis} /> : null}
        {analysis ? <FieldReportPanel analysis={analysis} /> : null}
        {digest ? <CivilActionDigestView digest={digest} /> : null}
        <ZoneTable zones={sitrep.zones} />
        <SectionList sections={sitrep.sections} />
        <SourceTable sources={sitrep.sources} />
      </div>

      <ContactBlock classification={sitrep.edition.classification} />
    </main>
  );
}
