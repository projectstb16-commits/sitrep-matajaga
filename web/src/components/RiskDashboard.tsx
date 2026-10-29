import { PILLAR_LABEL } from "@/lib/bands";
import type { PillarKey, Risk } from "@/types/sitrep";

import { BandIndicator } from "./BandIndicator";

const ORDER: PillarKey[] = [
  "security",
  "transport",
  "economy",
  "cyber",
  "weather",
];

/**
 * Risk Dashboard.
 *
 * Komposit ditampilkan sebagai angka utama, bukan sebagai grafik: satu skor
 * tunggal tidak memperoleh apa pun dari sumbu atau batang. Kelima pilar
 * ditempatkan sejajar di bawahnya agar pembaca melihat pilar mana yang
 * mengangkat komposit, bukan hanya hasil akhirnya.
 */
export function RiskDashboard({ risk }: { risk: Risk }) {
  return (
    <section aria-labelledby="risk-dashboard" className="mt-8">
      <h2 id="risk-dashboard" className="mb-3 text-lg font-bold text-[#0B1B3B]">
        Risk Dashboard
      </h2>

      <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_minmax(0,2.5fr)]">
        <div>
          <BandIndicator score={risk.composite} label="Composite" size="lg" />
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {ORDER.map((pillar) => (
            <BandIndicator
              key={pillar}
              score={risk.pillars[pillar]}
              label={PILLAR_LABEL[pillar]}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
