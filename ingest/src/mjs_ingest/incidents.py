"""Deteksi laporan kejadian lapangan dan pemetaannya terhadap rencana.

Rekap rengiat menyatakan apa yang direncanakan. Pesan susulan di grup relay
melaporkan apa yang terpantau: massa tiba, massa membubarkan diri, akses
jalan ditutup atau dibuka, situasi dinyatakan aman. Laporan susulan itu
berbentuk narasi bebas, tidak berformat, dan jumlahnya jauh lebih sedikit
daripada jumlah rencana.

Batas yang mengikat seluruh modul ini: **tidak adanya laporan bukan bukti
tidak terjadinya kegiatan.** Yang dapat dihitung hanyalah berapa rencana yang
memiliki laporan lapangan menyebut titiknya. Menyebut sisanya sebagai "batal"
atau menghitung "tingkat realisasi" akan mengubah ketiadaan pengamatan
menjadi temuan, dan pembaca akan menyimpulkan aksi tidak terjadi padahal yang
benar adalah tidak ada yang melaporkannya.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .places import canonical_point, expand_synonyms
from .whatsapp import Message, strip_phone_numbers

# Penanda keadaan lapangan. Satu pesan dapat membawa beberapa penanda.
SIGNALS: dict[str, re.Pattern[str]] = {
    "massa_tiba": re.compile(
        r"\bmassa\s+(?:mulai\s+)?(?:tiba|berkumpul|berorasi|bergerak|merapat)"
        r"|\bmulai\s+berorasi\b",
        re.IGNORECASE,
    ),
    "massa_bertahan": re.compile(r"\bmasih\s+bertahan\b|\bbertahan\s+di\b", re.IGNORECASE),
    "massa_bubar": re.compile(
        r"\b(?:telah\s+|sudah\s+)?membubarkan\s+diri\b|\bpembubaran\b|\bmassa\s+bubar\b",
        re.IGNORECASE,
    ),
    "situasi_aman": re.compile(
        r"\baman\s+(?:terkendali|kondusif)\b|\bsitkon\s+aman\b|\bsituasi\s+aman\b"
        r"|\bkondusif\b",
        re.IGNORECASE,
    ),
    "lalin_macet": re.compile(
        r"\bmacet\b|\bkemacetan\b|\bpadat\s+merayap\b|\btersendat\b", re.IGNORECASE
    ),
    # Jarak antara kata "akses" dan kata kerjanya kerap memuat nama jalan
    # yang bertitik ("Jl. Contoh"). Titik karena itu tidak boleh menjadi
    # pembatas; yang membatasi adalah akhir baris dan panjang jangkauan.
    "akses_ditutup": re.compile(
        r"\b(?:jalan|akses|ruas|jalur)[^\n;]{0,60}?\bdi\s?tutup\b"
        r"|\bpenutupan\s+(?:jalan|akses|ruas)\b"
        r"|\bpengalihan\s+arus\b",
        re.IGNORECASE,
    ),
    "akses_dibuka": re.compile(
        r"\b(?:jalan|akses|ruas|jalur)[^\n;]{0,60}?\bdi\s?buka\b"
        r"|\bakses\s+(?:kembali\s+)?normal\b|\bnormal\s+kembali\b"
        r"|\barus\s+(?:kembali\s+)?normal\b",
        re.IGNORECASE,
    ),
    "nihil": re.compile(r"\bnihil\b|\btidak\s+ada\s+kegiatan\b", re.IGNORECASE),
}

# Penanda yang menunjukkan pesan melaporkan keadaan, bukan merencanakan.
_FIELD_SIGNALS = (
    "massa_tiba",
    "massa_bertahan",
    "massa_bubar",
    "situasi_aman",
    "lalin_macet",
    "akses_ditutup",
    "akses_dibuka",
)

REPORT_TIME = re.compile(r"[Pp]ukul\s*(\d{1,2})[.:](\d{2})\s*WIB")

# Nama jalan adalah rangkaian kata berawalan huruf besar, kerap memuat
# singkatan bertitik ("Jl. HR. Rasuna Said"). Pengambilan berhenti pada kata
# berhuruf kecil pertama, karena di situlah nama berakhir dan kalimat
# berlanjut; tanpa batas itu nama ruas terbaca "Contoh Satu sudah di buka".
ROAD = re.compile(
    r"\b(?:Jl\.?|Jalan)\s+"
    # Kapitalisasi pada laporan lapangan tidak konsisten ("Jl. Imam bonjol"),
    # sehingga kata berhuruf kecil ikut diambil lebih dahulu, lalu dipangkas.
    r"((?:[A-Z][A-Za-z0-9]*\.?)(?:\s+(?:[A-Z][A-Za-z0-9]*\.?|[a-z]{3,})){0,6})"
)

# Kata fungsi, kata kerja keadaan, dan keterangan arah bukan bagian nama ruas.
# Nama dipangkas dari kedua ujung selama ujungnya masih berupa kata semacam
# itu, karena nama ruas pada laporan lapangan menyatu dengan kalimatnya.
_ROAD_STOP = frozenset(
    {
        "dari", "dan", "menuju", "no", "arah", "serta", "sampai", "hingga",
        "ke", "sudah", "telah", "akan", "masih", "sedang", "kembali", "dibuka",
        "ditutup", "buka", "tutup", "normal", "tidak", "belum", "dengan",
        "untuk", "pada", "oleh", "yang", "ini", "itu", "saat", "di", "ada",
        "dalam", "serah", "terpantau", "macet", "lancar", "padat",
    }
)


# Rekap rencana memakai bentuk butir yang khas; pesan semacam itu bukan
# laporan kejadian walau memuat kata "macet" pada kolom kerawanan.
_IS_PLAN = re.compile(
    r"^\s*\*?\s*\d{1,3}\.?\s*\*?\s*Pukul\b", re.IGNORECASE | re.MULTILINE
)


@dataclass
class FieldReport:
    """Satu laporan keadaan lapangan."""

    reported_on: str
    reported_time: str | None
    point_keys: list[str]
    signals: list[str]
    roads: list[str]
    excerpt: str
    sender_token: str

    @property
    def affects_traffic(self) -> bool:
        return any(
            s in self.signals for s in ("lalin_macet", "akses_ditutup", "akses_dibuka")
        )


@dataclass
class PlanMatch:
    """Satu rencana beserta laporan lapangan yang menyebut titiknya."""

    plan: dict[str, Any]
    point_key: str | None
    reports: list[FieldReport] = field(default_factory=list)

    @property
    def observed(self) -> bool:
        return bool(self.reports)


def detect_reports(
    messages: list[Message], known_points: set[str]
) -> list[FieldReport]:
    """Kumpulkan laporan keadaan dari pesan susulan.

    ``known_points`` adalah kunci titik yang dikenal dari rekap rencana.
    Penyebutan titik pada narasi dicocokkan terhadap daftar itu, sehingga
    tidak ada titik baru yang lahir dari potongan kalimat.
    """
    out: list[FieldReport] = []

    for message in messages:
        body = message.body
        if _IS_PLAN.search(body):
            continue

        signals = [name for name, pat in SIGNALS.items() if pat.search(body)]
        if not any(s in _FIELD_SIGNALS for s in signals):
            continue

        time_match = REPORT_TIME.search(body)
        excerpt = strip_phone_numbers(" ".join(body.split()))[:280]

        out.append(
            FieldReport(
                reported_on=message.sent.isoformat(),
                reported_time=(
                    f"{int(time_match.group(1)):02d}:{time_match.group(2)}"
                    if time_match
                    else None
                ),
                point_keys=_points_in(body, known_points),
                signals=sorted(signals),
                roads=_roads_in(body),
                excerpt=excerpt,
                sender_token=_token(message.sender),
            )
        )

    return out


def _points_in(body: str, known_points: set[str]) -> list[str]:
    haystack = canonical_haystack(body)
    found = [key for key in known_points if key and f" {key} " in haystack]
    # Kunci yang merupakan bagian dari kunci lain tidak dihitung dua kali.
    return sorted(
        key for key in found if not any(key != other and key in other for other in found)
    )


def canonical_haystack(body: str) -> str:
    """Bentuk teks narasi agar sebanding dengan kunci titik.

    Penyeragaman yang sama dengan kunci titik diterapkan di sini. Tanpa itu,
    narasi yang menulis "Kemen ESDM" tidak akan pernah cocok dengan kunci
    "kementerian esdm" yang berasal dari rekap rencana.
    """
    lowered = re.sub(r"[^a-z0-9. ]+", " ", body.lower())
    lowered = expand_synonyms(re.sub(r"\s+", " ", lowered))
    return " " + lowered + " "


def _roads_in(body: str) -> list[str]:
    roads: list[str] = []
    for match in ROAD.finditer(body):
        name = _trim_road(match.group(1))
        if name and name not in roads:
            roads.append(name)
    return roads[:8]


def _trim_road(raw: str) -> str | None:
    """Pangkas kata fungsi dari kedua ujung nama ruas."""
    words = re.sub(r"\s+", " ", raw.strip()).split()
    while words and words[0].lower().rstrip(".") in _ROAD_STOP:
        words.pop(0)
    while words and words[-1].lower().rstrip(".") in _ROAD_STOP:
        words.pop()
    name = " ".join(words).rstrip(".")
    return name if len(name) > 2 else None


def _token(sender: str) -> str:
    from .whatsapp import sender_token

    return sender_token(sender)


def match_plans(
    plans: list[dict[str, Any]], reports: list[FieldReport]
) -> list[PlanMatch]:
    """Pasangkan rencana dengan laporan lapangan pada tanggal dan titik sama."""
    by_date: dict[str, list[FieldReport]] = {}
    for report in reports:
        by_date.setdefault(report.reported_on, []).append(report)

    matches: list[PlanMatch] = []
    for plan in plans:
        key = canonical_point(plan.get("location"))
        day = plan.get("activity_date")
        candidates = by_date.get(str(day), []) if day else []
        matches.append(
            PlanMatch(
                plan=plan,
                point_key=key,
                reports=[r for r in candidates if key and key in r.point_keys],
            )
        )
    return matches


def observation_summary(matches: list[PlanMatch]) -> dict[str, Any]:
    """Ringkas seberapa banyak rencana yang memiliki laporan lapangan.

    Bidang sengaja dinamai "dengan laporan" dan "tanpa laporan", bukan
    "terlaksana" dan "batal". Yang diamati adalah ada tidaknya laporan.
    """
    observed = [m for m in matches if m.observed]
    return {
        "plans": len(matches),
        "plans_with_field_report": len(observed),
        "plans_without_field_report": len(matches) - len(observed),
        "note": (
            "Tidak adanya laporan lapangan bukan bukti kegiatan tidak terjadi. "
            "Grup relay melaporkan sebagian kecil kegiatan saja."
        ),
    }
