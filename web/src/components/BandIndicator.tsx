import { BAND_FILL, BAND_INK, BAND_LABEL, bandOf } from "@/lib/bands";

/**
 * Penanda band untuk satu skor.
 *
 * Isian warna mengikuti brand standard, tetapi warna tidak pernah menjadi
 * satu-satunya pembawa informasi. Angka dan nama band selalu ditulis.
 * Pemeriksaan palet menunjukkan isian HIGH dan CRITICAL hanya berjarak
 * ΔE 4.2 pada penglihatan normal, jauh di bawah ambang yang dapat dibedakan
 * dengan percaya diri; justru dua band itu yang paling menentukan keputusan.
 * Lihat catatan palet pada docs/doctrine/brand-standard.md.
 */
export function BandIndicator({
  score,
  label,
  size = "sm",
}: {
  score: number;
  label?: string;
  size?: "sm" | "lg";
}) {
  const band = bandOf(score);
  const large = size === "lg";

  return (
    <div
      className={
        large
          ? "rounded-sm border-l-4 px-4 py-3"
          : "rounded-sm border-l-4 px-3 py-2"
      }
      style={{
        backgroundColor: BAND_FILL[band],
        borderLeftColor: BAND_INK[band],
      }}
    >
      {label ? (
        <div className="text-[11px] font-bold uppercase tracking-wide text-[#3d4350]">
          {label}
        </div>
      ) : null}
      <div className="flex items-baseline gap-2">
        <span
          className={
            large
              ? "text-4xl font-bold tabular-nums"
              : "text-xl font-bold tabular-nums"
          }
          style={{ color: BAND_INK[band] }}
        >
          {score}
        </span>
        <span
          className={
            large
              ? "text-sm font-bold uppercase"
              : "text-xs font-bold uppercase"
          }
          style={{ color: BAND_INK[band] }}
        >
          {BAND_LABEL[band]}
        </span>
      </div>
    </div>
  );
}
