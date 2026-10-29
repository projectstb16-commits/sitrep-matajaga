import { BRAND } from "@/lib/bands";

/** Blok kontak penerbit. Wajib pada setiap produk. */
export function ContactBlock({ classification }: { classification: string }) {
  return (
    <footer
      style={{ backgroundColor: BRAND.navy }}
      className="mt-10 text-white"
    >
      <div className="mx-auto max-w-6xl px-6 py-6 text-sm">
        <p className="font-bold">
          Matajaga Research — Strategic Risk &amp; Intelligence Unit
        </p>
        <p className="text-[#c9cfdb]">
          PT HRM Multi Sinergy &nbsp;|&nbsp; Direktur: Toni Hendrawan
        </p>
        <p className="text-[#c9cfdb]">
          Email: research@matajaga.id &nbsp;|&nbsp; Operations: ops@matajaga.id
        </p>
        <p className="text-[#c9cfdb]">
          Editorial revisions / errata: editorial@matajaga.id
        </p>

        {classification === "PREVIEW_OPEN_REDISTRIBUTION" ? (
          <p
            className="mt-4 border-t pt-3 text-[#9aa4b8]"
            style={{ borderColor: BRAND.gold }}
          >
            PREVIEW edition: open redistribution permitted with attribution. For
            Tier-A Client Edition, contact issuer for activation protocol.
          </p>
        ) : null}
      </div>
    </footer>
  );
}
