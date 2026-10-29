"""Kanonikalisasi titik aksi dan gazetteer koordinat.

Satu titik yang sama ditulis bermacam-macam pada laporan lapangan: "Depan KPK
RI Jl. Kuningan Persada Jaksel", "Kantor KPK RI", "KPK RI". Tanpa
penyeragaman, satu titik terhitung sebagai beberapa dan peringkat titik rawan
menjadi salah.

Koordinat tidak ditetapkan modul ini. Gazetteer menyimpan koordinat beserta
asalnya, dan entri tanpa koordinat tetap bernilai ``None``. Koordinat yang
ditulis dari ingatan tanpa sumber adalah angka karangan, dan pembaca yang
memakainya untuk rencana lalu lintas akan diarahkan ke tempat yang salah.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Kata yang menerangkan posisi relatif terhadap titik, bukan nama titiknya.
_PREFIX = re.compile(
    r"\b(depan|dpn|sekitar|kawasan|area|halaman|pelataran|seberang|kantor|"
    r"kantor pusat|gd\.?|gedung|komplek|kompleks|bundaran|simpang)\b",
    re.IGNORECASE,
)

# Nama jalan menerangkan letak, dan satu titik dapat ditulis dengan jalan yang
# berbeda-beda. Nama jalan karena itu tidak masuk kunci titik.
_STREET = re.compile(
    r"\bjl\.?\s*[^,/&]*|\bjalan\s+[^,/&]*", re.IGNORECASE
)

_REGION_TAIL = re.compile(
    r"\b(jakpus|jaksel|jaktim|jakbar|jakut|jakarta pusat|jakarta selatan|"
    r"jakarta timur|jakarta barat|jakarta utara|jakarta|tangsel|tangerang|"
    r"bekasi|depok|bogor|kel\.\s*\w+|kec\.\s*\w+)\b",
    re.IGNORECASE,
)

_NOISE = re.compile(r"[^a-z0-9. ]+")

# Penyeragaman penulisan yang berbeda untuk lembaga yang sama.
_SYNONYM: dict[str, str] = {
    "kemen esdm": "kementerian esdm",
    "kemen atr": "kementerian atr",
    "kemen lingkungan hidup": "kementerian lingkungan hidup",
    "kemendikti saintek": "kementerian dikti saintek",
    "kemendikdasmen": "kementerian dikdasmen",
    "kemenkes": "kementerian kesehatan",
    "kemenag": "kementerian agama",
    "gd. dpr": "dpr mpr ri",
    "dpr": "dpr mpr ri",
    "dpr mpr": "dpr mpr ri",
    "mpr": "dpr mpr ri",
}


@dataclass
class Place:
    """Satu titik pada gazetteer.

    ``lat``/``lon`` bernilai ``None`` sampai diisi dari sumber yang disebut
    pada ``source``. Entri tanpa koordinat tetap dipakai untuk peringkat titik
    rawan; yang tidak dapat dilakukan tanpa koordinat hanyalah penempatan
    pada peta.
    """

    key: str
    label: str
    aliases: list[str] = field(default_factory=list)
    lat: float | None = None
    lon: float | None = None
    source: str | None = None
    verified_at: str | None = None

    @property
    def located(self) -> bool:
        return self.lat is not None and self.lon is not None


@dataclass
class PointStat:
    """Hitungan kegiatan pada satu titik."""

    key: str
    label: str
    actions: int
    crowd_reported: int
    dates: list[str]
    located: bool = False
    lat: float | None = None
    lon: float | None = None

    @property
    def recurring(self) -> bool:
        """Titik yang dipakai pada lebih dari satu hari."""
        return len(set(self.dates)) > 1


def expand_synonyms(text: str) -> str:
    """Seragamkan penulisan lembaga pada teks bebas."""
    for pattern, replacement in _SYNONYM.items():
        text = re.sub(rf"\b{re.escape(pattern)}\b", replacement, text)
    return re.sub(r"\s+", " ", text)


def canonical_point(location: str | None) -> str | None:
    """Turunkan kunci titik dari lokasi yang ditulis bebas."""
    if not location:
        return None

    text = unicodedata.normalize("NFKC", location).lower()
    # Lokasi gabungan ("A & B", "A/ B") memakai penyebutan pertama sebagai
    # titik awal; penyebutan berikutnya adalah tujuan lanjutan aksi.
    text = re.split(r"[/&]|\bdan\b", text)[0]
    text = _STREET.sub(" ", text)
    text = _PREFIX.sub(" ", text)
    text = _REGION_TAIL.sub(" ", text)
    text = _NOISE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip(" .")

    for pattern, replacement in _SYNONYM.items():
        if re.fullmatch(rf"{re.escape(pattern)}(\s+ri)?", text):
            return replacement
        text = re.sub(rf"\b{re.escape(pattern)}\b", replacement, text)

    text = re.sub(r"\s+", " ", text).strip(" .")
    return text or None


# Akronim lembaga ditulis dengan huruf besar. Tanpa daftar ini label
# terbaca "Kedubes Rrt" dan "Kementerian Esdm", yang tidak layak terbit.
ACRONYM = frozenset(
    {
        "ri", "dki", "rrt", "esdm", "atr", "bpn", "kpk", "kpu", "ojk", "bni",
        "bri", "bca", "btn", "dpr", "mpr", "dpd", "dprd", "pln", "kkp", "bpk",
        "bpjs", "tni", "ham", "komnas", "gbk", "scbd", "mrt", "lrt", "bumn",
        "pt", "cv", "ui", "itb", "unj", "iup",
    }
)


def label_for(key: str) -> str:
    """Bentuk label yang terbaca dari kunci titik."""
    words = []
    for word in key.split():
        bare = word.rstrip(".")
        if bare in ACRONYM:
            words.append(bare.upper() + ("." if word.endswith(".") else ""))
        else:
            words.append(word.capitalize())
    return " ".join(words)


def rank_points(actions: list[dict[str, Any]], gazetteer: dict[str, Place]) -> list[PointStat]:
    """Peringkat titik menurut jumlah kegiatan, terbanyak lebih dahulu."""
    bucket: dict[str, PointStat] = {}

    for action in actions:
        key = canonical_point(action.get("location"))
        if key is None:
            continue
        place = gazetteer.get(key)
        stat = bucket.get(key)
        if stat is None:
            stat = PointStat(
                key=key,
                label=place.label if place else label_for(key),
                actions=0,
                crowd_reported=0,
                dates=[],
                located=place.located if place else False,
                lat=place.lat if place else None,
                lon=place.lon if place else None,
            )
            bucket[key] = stat
        stat.actions += 1
        crowd = action.get("crowd_reported")
        if isinstance(crowd, int):
            stat.crowd_reported += crowd
        if action.get("activity_date"):
            stat.dates.append(str(action["activity_date"]))

    return sorted(bucket.values(), key=lambda s: (-s.actions, s.key))


def load_gazetteer(path: str | Path) -> dict[str, Place]:
    """Baca gazetteer. Berkas yang belum ada menghasilkan gazetteer kosong."""
    file = Path(path)
    if not file.exists():
        return {}
    payload = json.loads(file.read_text(encoding="utf-8"))
    out: dict[str, Place] = {}
    for entry in payload.get("places", []):
        place = Place(**entry)
        out[place.key] = place
        for alias in place.aliases:
            out.setdefault(alias, place)
    return out


def merge_gazetteer(
    existing: dict[str, Place], points: list[PointStat]
) -> tuple[list[Place], int]:
    """Tambahkan titik baru ke gazetteer tanpa menyentuh koordinat yang ada.

    Koordinat yang sudah diisi analis tidak pernah ditimpa. Yang ditambahkan
    hanya entri untuk titik yang belum dikenal, dengan koordinat kosong.
    """
    by_key: dict[str, Place] = {}
    for place in existing.values():
        by_key[place.key] = place

    added = 0
    for point in points:
        if point.key in by_key:
            continue
        by_key[point.key] = Place(key=point.key, label=point.label)
        added += 1

    return sorted(by_key.values(), key=lambda p: p.key), added


def gazetteer_json(places: list[Place]) -> str:
    payload = {
        "note": (
            "Koordinat diisi dari sumber yang disebut pada 'source'. Entri tanpa "
            "koordinat tidak ditempatkan pada peta dan tetap muncul pada "
            "peringkat titik rawan."
        ),
        "places": [asdict(p) for p in places],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def coverage(points: list[PointStat]) -> dict[str, int]:
    """Berapa banyak kegiatan yang titiknya sudah berkoordinat."""
    total = sum(p.actions for p in points)
    located = sum(p.actions for p in points if p.located)
    return {
        "points": len(points),
        "points_located": sum(1 for p in points if p.located),
        "actions": total,
        "actions_located": located,
    }
