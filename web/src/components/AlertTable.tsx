import { TableScroll } from "./TableScroll";

import { BAND_FILL, BAND_INK, BRAND, bandOf } from "@/lib/bands";
import type { Alert } from "@/types/sitrep";

import { ClaimTagMark } from "./ClaimTagMark";

const HORIZON_ORDER = ["0-6h", "0-24h", "0-72h", "0-30d"] as const;

/** Critical Alerts, diurutkan dari horizon terdekat. */
export function AlertTable({ alerts }: { alerts: Alert[] }) {
  const sorted = [...alerts].sort(
    (a, b) =>
      HORIZON_ORDER.indexOf(a.horizon) - HORIZON_ORDER.indexOf(b.horizon),
  );

  return (
    <section aria-labelledby="critical-alerts" className="mt-10">
      <h2
        id="critical-alerts"
        className="mb-3 text-lg font-bold text-[#0B1B3B]"
      >
        Critical Alerts
      </h2>

      {sorted.length === 0 ? (
        <p className="border-l-4 border-[#dfe3ea] bg-white px-3 py-2 text-sm text-[#3d4350]">
          Tidak ada alert pada edisi ini.
        </p>
      ) : (
        <TableScroll>
          <table className="w-full min-w-[44rem] border-collapse text-sm">
            <thead>
              <tr
                style={{ backgroundColor: BRAND.navy }}
                className="text-white"
              >
                <th className="w-24 px-3 py-2 font-bold">Horizon</th>
                <th className="px-3 py-2 font-bold">Headline</th>
                <th className="w-20 px-3 py-2 text-right font-bold">Skor</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((alert, i) => {
                const band =
                  alert.score === undefined ? null : bandOf(alert.score);
                return (
                  <tr
                    key={`${alert.horizon}-${i}`}
                    className="border-b border-[#dfe3ea] bg-white"
                  >
                    <td className="px-3 py-2 font-bold tabular-nums text-[#16181d]">
                      {alert.horizon}
                    </td>
                    <td className="px-3 py-2">
                      <ClaimTagMark tag={alert.claim_tag} />
                      <span className="font-bold text-[#16181d]">
                        {alert.headline}
                      </span>
                      {alert.detail ? (
                        <p className="mt-1 text-[#3d4350]">{alert.detail}</p>
                      ) : null}
                    </td>
                    <td
                      className="px-3 py-2 text-right font-bold tabular-nums"
                      style={
                        band
                          ? {
                              backgroundColor: BAND_FILL[band],
                              color: BAND_INK[band],
                            }
                          : undefined
                      }
                    >
                      {alert.score ?? "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </TableScroll>
      )}
    </section>
  );
}
