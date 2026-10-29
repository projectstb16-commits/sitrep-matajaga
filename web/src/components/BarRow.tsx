import { BRAND } from "@/lib/bands";

/**
 * Satu baris batang untuk deret tunggal.
 *
 * Deret tunggal tidak memerlukan legenda: judul bagian sudah menamainya.
 * Nilai ditulis di ujung batang, bukan pada setiap sumbu, agar angka terbaca
 * tanpa menambah garis bantu.
 */
export function BarRow({
  label,
  value,
  max,
  caption,
}: {
  label: string;
  value: number;
  max: number;
  caption?: string;
}) {
  const share =
    max > 0 ? Math.max((value / max) * 100, value > 0 ? 1.5 : 0) : 0;

  return (
    <div className="flex items-center gap-3 py-1">
      <div className="w-28 shrink-0 text-right text-sm tabular-nums text-[#3d4350]">
        {label}
      </div>
      <div className="flex min-w-0 flex-1 items-center gap-2">
        <div
          className="h-3 rounded-r-sm"
          style={{ width: `${share}%`, backgroundColor: BRAND.navy }}
        />
        <span className="shrink-0 text-sm font-bold tabular-nums text-[#16181d]">
          {value.toLocaleString("id-ID")}
        </span>
        {caption ? (
          <span className="truncate text-xs text-[#6b7280]">{caption}</span>
        ) : null}
      </div>
    </div>
  );
}
