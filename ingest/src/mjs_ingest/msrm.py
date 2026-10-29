"""MSRM v1.1 — skala risiko, pembobotan pilar, dan token warna band.

Modul ini stdlib murni dan tidak mengimpor apa pun dari paket lain, sehingga
dapat dipakai baik oleh jalur validasi maupun oleh perkakas lain tanpa
menyeret dependensi dokumen.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

METHODOLOGY = "MSRM v1.1"

PILLARS = ("security", "transport", "economy", "cyber", "weather")

HORIZONS = ("0-6h", "0-24h", "0-72h", "0-30d")

CLAIM_TAGS = ("FACT", "ANALYSIS", "ASSUMPTION")

RELIABILITY_TIERS = ("A1", "B2", "B3", "C3")


class Band(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Batas bawah inklusif per band. Urut menurun agar pencarian band berhenti
# pada ambang pertama yang terlampaui.
_BAND_FLOORS: tuple[tuple[int, Band], ...] = (
    (80, Band.CRITICAL),
    (60, Band.HIGH),
    (40, Band.MODERATE),
    (0, Band.LOW),
)

# Isian lembut per band. Nilai yang sama dipakai dashboard (web/src/lib/bands.ts)
# supaya dokumen terbit dan tampilan layar tidak menyimpang.
BAND_FILL: dict[Band, str] = {
    Band.LOW: "#DDEFD5",
    Band.MODERATE: "#FBF2CC",
    Band.HIGH: "#FADFC5",
    Band.CRITICAL: "#F7D3D3",
}

BRAND_NAVY = "#0B1B3B"
BRAND_GOLD = "#B8860B"

# Status: provisional. Doktrin MSRM v1.1 menetapkan skala dan daftar pilar,
# tidak menetapkan bobot komposit. Lihat docs/doctrine/msrm-v1.1.md.
DEFAULT_WEIGHTS: dict[str, float] = {
    "security": 0.30,
    "transport": 0.25,
    "economy": 0.20,
    "cyber": 0.15,
    "weather": 0.10,
}


class ScoreOutOfRange(ValueError):
    """Skor di luar rentang 0-100."""


def band_of(score: int) -> Band:
    """Kembalikan band MSRM untuk sebuah skor."""
    _check_score(score)
    for floor, band in _BAND_FLOORS:
        if score >= floor:
            return band
    raise AssertionError("unreachable: _BAND_FLOORS harus mencakup 0")


def fill_of(score: int) -> str:
    """Kembalikan warna isian band untuk sebuah skor."""
    return BAND_FILL[band_of(score)]


@dataclass(frozen=True)
class Composite:
    """Hasil perhitungan komposit beserta jejak keputusannya."""

    score: int
    band: Band
    weighted_raw: float
    floored_by: str | None

    @property
    def was_floored(self) -> bool:
        return self.floored_by is not None


def composite(
    pillars: dict[str, int],
    weights: dict[str, float] | None = None,
) -> Composite:
    """Hitung skor komposit dari lima pilar.

    Rata-rata berbobot dapat meredam satu pilar ekstrem sampai menyesatkan,
    sehingga berlaku aturan pengaman: bila ada pilar pada band CRITICAL,
    komposit tidak dilaporkan di bawah ambang HIGH. Pilar yang memicu
    pengangkatan dicatat pada ``floored_by`` agar keputusan itu dapat diaudit,
    bukan tersembunyi di dalam satu angka.
    """
    missing = sorted(set(PILLARS) - set(pillars))
    if missing:
        raise ValueError(f"pilar belum lengkap: {', '.join(missing)}")

    unknown = sorted(set(pillars) - set(PILLARS))
    if unknown:
        raise ValueError(f"pilar tidak dikenal: {', '.join(unknown)}")

    for name, value in pillars.items():
        _check_score(value, label=name)

    active = dict(weights) if weights is not None else dict(DEFAULT_WEIGHTS)
    total_weight = sum(active.values())
    if total_weight <= 0:
        raise ValueError("total bobot harus lebih besar dari nol")

    weighted_raw = sum(pillars[p] * active.get(p, 0.0) for p in PILLARS) / total_weight
    score = round(weighted_raw)

    floored_by: str | None = None
    critical = [p for p in PILLARS if band_of(pillars[p]) is Band.CRITICAL]
    if critical and score < 60:
        score = 60
        floored_by = critical[0] if len(critical) == 1 else ", ".join(critical)

    return Composite(
        score=score,
        band=band_of(score),
        weighted_raw=weighted_raw,
        floored_by=floored_by,
    )


def _check_score(value: object, label: str = "skor") -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ScoreOutOfRange(f"{label} harus bilangan bulat, diterima {value!r}")
    if not 0 <= value <= 100:
        raise ScoreOutOfRange(f"{label} di luar rentang 0-100: {value}")
