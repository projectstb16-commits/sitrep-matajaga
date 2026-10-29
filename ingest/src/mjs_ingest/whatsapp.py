"""Ekstraksi rencana kegiatan unjuk rasa dari ekspor chat WhatsApp.

Grup relay membagikan rekap "rengiat" dalam dua format yang keduanya ditangani
di sini:

Format berlabel (paling umum), satu kegiatan satu baris::

    *1.* Pukul 13.00 WIB, Tempat <lokasi>, Pelaksana <organisasi>,
    Pimpinan <nama>, Jumlah ± 100 Orang, Bentuk giat Unjuk rasa,
    Tuntutan <tuntutan>.

Format bernomor, satu kegiatan beberapa baris, di bawah judul kecamatan::

    *GAMBIR* :

    1.Pukul 13.00 WIB, <lokasi>
    <organisasi>
    Pj. <nama>, kl. 15 orang.
    "<tuntutan>"

Urutan label pada format pertama tidak tetap — pada butir giat masyarakat,
"Bentuk giat" mendahului "Pimpinan". Karena itu label dicari berdasarkan
posisinya di dalam teks, bukan berdasarkan urutan yang diandaikan.

Dua hal yang sengaja tidak dilakukan modul ini:

Modul ini tidak menilai risiko. Jumlah massa yang terbaca adalah angka yang
dilaporkan relay, bukan skor. Menurunkan skor pilar dari jumlah massa akan
menghasilkan penilaian yang tidak berasal dari analis mana pun.

Modul ini menyunting nama penanggung jawab secara bawaan. Nama itu milik orang
yang dapat diidentifikasi, dan rekap ini beredar di luar kendali penerbit.
Penyertaan nama harus merupakan keputusan sadar, bukan keadaan bawaan.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Literal

# Jenis kegiatan tidak pernah ditebak. Rekap memuat konser, lomba lari, dan
# wisuda dengan massa puluhan ribu; bila jenis yang tidak tertulis diisi
# "unjuk rasa" sebagai bawaan, jumlah massa aksi terbaca berlipat dan
# pembaca menyimpulkan tekanan yang tidak ada.
ActivityKind = Literal[
    "unjuk_rasa", "giat_masyarakat", "giat_kepolisian", "tidak_ditentukan"
]

# Penanda pada bidang "Bentuk giat", yang menyebut jenis kegiatan langsung.
UNRAS_WORDS = re.compile(r"\b(unjuk\s*rasa|unras|aksi\s+damai|demo\w*)\b", re.IGNORECASE)

# Baris kepala pesan pada ekspor WhatsApp: "18/10/26 21.25 - Pengirim: isi"
MESSAGE_HEAD = re.compile(
    r"^(?P<date>\d{2}/\d{2}/\d{2}) (?P<time>\d{2}\.\d{2}) - (?P<sender>[^:\n]{1,60}): ",
    re.MULTILINE,
)

BULAN = {
    "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6,
    "juli": 7, "agustus": 8, "september": 9, "oktober": 10, "november": 11,
    "desember": 12, "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7,
    "agu": 8, "ags": 8, "sep": 9, "okt": 10, "nov": 11, "des": 12,
}

HEADER_DATE = re.compile(
    r"(\d{1,2})\s+([A-Za-z]+)\.?\s*(\d{4})",
)

# Wilayah ditulis dengan berbagai singkatan di lapangan ("Jaksel", "Jakarta
# Selatan", "Jak-Sel"). Alias dipetakan ke kode zona Jabodetabek agar satu
# wilayah tidak terhitung sebagai beberapa. Alias yang lebih panjang diuji
# lebih dahulu supaya "Jakarta Selatan" tidak tertangkap oleh "Jakarta".
REGION_ALIAS: dict[str, str] = {
    "jakarta pusat": "JAKPUS", "jakpus": "JAKPUS", "jak-pus": "JAKPUS",
    "jakarta utara": "JAKUT", "jakut": "JAKUT", "jak-ut": "JAKUT",
    "jakarta barat": "JAKBAR", "jakbar": "JAKBAR", "jak-bar": "JAKBAR",
    "jakarta selatan": "JAKSEL", "jaksel": "JAKSEL", "jak-sel": "JAKSEL",
    "jakarta timur": "JAKTIM", "jaktim": "JAKTIM", "jak-tim": "JAKTIM",
    "kepulauan seribu": "KEP_SERIBU", "kep. seribu": "KEP_SERIBU",
    "tangerang selatan": "TANGSEL", "tangsel": "TANGSEL",
    "kota tangerang": "TANGERANG", "kab. tangerang": "TANGERANG",
    "tangerang": "TANGERANG",
    "kota bekasi": "BEKASI", "kab. bekasi": "BEKASI", "bekasi": "BEKASI",
    "kota bogor": "BOGOR", "kab. bogor": "BOGOR", "bogor": "BOGOR",
    "depok": "DEPOK",
}

_ALIAS_ORDER = sorted(REGION_ALIAS, key=len, reverse=True)

LABELED_ITEM = re.compile(r"^\*\s*(\d{1,3})\.?\s*\*\s*(.+)$", re.MULTILINE)
NUMBERED_ITEM = re.compile(r"^\s*(\d{1,3})\s*\.\s*Pukul\b", re.IGNORECASE | re.MULTILINE)

KECAMATAN_HEADING = re.compile(r"^\*\s*([A-Z][A-Z .\-]{2,40}?)\s*\*\s*:\s*$", re.MULTILINE)

# Judul seksi memakai bentuk yang sama dengan judul kecamatan. Tanpa penapis
# ini, "RENCANA KEGIATAN SIDANG" akan tercatat sebagai nama wilayah.
NOT_AN_AREA = re.compile(
    r"^(RENCANA|RENGIAT|UNRAS|GIAT|KEGIATAN|CATATAN|POIN|ALAT)\b", re.IGNORECASE
)

# Penanda seksi harus berdiri sendiri sebagai satu baris. Tanpa pembatas ini,
# judul pesan "Rengiat Unras dan masyarakat wil ..." ikut terbaca sebagai
# penanda, dan seluruh butir sesudahnya mewarisi jenis unjuk rasa.
SECTION_UNRAS = re.compile(
    r"^\*?\s*(?:[A-Z]\.\s*)?(?:RENGIAT\s+)?Unras\s*:?\s*(?:\d+\s*GIAT)?\s*\*?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
SECTION_GIAT = re.compile(
    r"^\*?\s*(?:[A-Z]\.\s*)?(?:RENGIAT\s+)?Giat\s+masyarakat\s*:?\s*"
    r"(?:\d+\s*GIAT)?\s*\*?\s*$"
    r"|^\*?\s*[A-Z]\.\s*RENGIAT\s+MASYARAKAT\s*:?\s*(?:\d+\s*GIAT)?\s*\*?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
SECTION_POLRI = re.compile(
    r"^\*?\s*[A-Z]\.\s*RENGIAT\s+KEPOLISIAN\s*:?\s*(?:\d+\s*GIAT)?\s*\*?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Laporan naratif memakai penomoran Romawi untuk bagian ("*I. WAKTU :*") dan
# angka untuk sub-bidang di dalamnya. Baris "2. Pukul : ..." di sana adalah
# keterangan waktu satu kegiatan, bukan kegiatan kedua.
ROMAN_SECTION = re.compile(r"^\*\s*(?:I{1,3}|IV|V|VI{0,3})\.\s*[A-Z]", re.MULTILINE)

TIME_RANGE = re.compile(
    r"Pukul\s*(\d{1,2})\s*[.:]\s*(\d{2})"
    r"(?:\s*[-–]\s*(\d{1,2})\s*[.:]\s*(\d{2}))?\s*WIB",
    re.IGNORECASE,
)

LABELS = ("Tempat", "Pelaksana", "Pimpinan", "Jumlah", "Bentuk giat", "Tuntutan")
LABEL_FIND = re.compile(
    r"(?:^|,)\s*(Tempat|Pelaksana|Pimpinan|Jumlah|Bentuk giat|Tuntutan)\s+",
    re.IGNORECASE,
)

CROWD = re.compile(r"(?:±\s*|kl\.?\s*|sekitar\s*)?([\d][\d.,]*)\s*[Oo]rang")
PJ_LINE = re.compile(r"^\s*p\.?j\.?\s*\.?\s*(?P<name>.+?)\s*,\s*(?P<crowd>.+?)\s*\.?\s*$", re.IGNORECASE)

# Nomor Indonesia ditulis sebagai +62..., 62..., atau 08... pada data lapangan.
PHONE = re.compile(r"(?:\+?62|\b0)[\s\-]?\d[\d\s\-]{7,}\d")


@dataclass(frozen=True)
class Message:
    sent: date
    sender: str
    body: str


@dataclass
class CivilAction:
    """Satu kegiatan sebagaimana dilaporkan relay.

    Setiap bidang adalah kutipan dari laporan, bukan hasil penilaian. Bidang
    yang tidak tercantum pada laporan bernilai ``None`` dan tidak diisi dugaan.
    """

    activity_date: str | None
    region: str | None
    area: str | None
    time_start: str | None
    time_end: str | None
    location: str | None
    organizer: str | None
    leader: str | None
    crowd_reported: int | None
    kind: ActivityKind
    demand: str | None
    reported_on: str = ""
    source_format: Literal["berlabel", "bernomor"] = "berlabel"
    issues: list[str] = field(default_factory=list)

    def redacted(self) -> CivilAction:
        """Salinan tanpa nama penanggung jawab."""
        return CivilAction(**{**self.__dict__, "leader": None})


def parse_messages(text: str) -> list[Message]:
    """Pecah ekspor WhatsApp menjadi pesan."""
    out: list[Message] = []
    heads = list(MESSAGE_HEAD.finditer(text))
    for i, head in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        sent = _export_date(head["date"])
        if sent is None:
            continue
        out.append(
            Message(sent=sent, sender=head["sender"].strip(), body=text[head.end() : end])
        )
    return out


@dataclass
class Extraction:
    """Hasil ekstraksi beserta apa yang tidak terpakai.

    Baris yang dilewati ikut dilaporkan. Rekap rengiat beredar bersama pesan
    biasa yang kebetulan bernomor, dan menyimpan keduanya tanpa pembeda akan
    menghasilkan rekaman setengah kosong yang terlihat seperti data.
    """

    actions: list[CivilAction] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    def redacted(self) -> Extraction:
        return Extraction(
            actions=[a.redacted() for a in self.actions], skipped=list(self.skipped)
        )


def extract(messages: list[Message]) -> Extraction:
    """Kumpulkan seluruh kegiatan dari pesan yang memuat rekap rengiat."""
    result = Extraction()
    for message in messages:
        _actions_in(message, result)
    return result


def extract_actions(messages: list[Message]) -> list[CivilAction]:
    """Jalan pintas bila laporan baris terlewat tidak diperlukan."""
    return extract(messages).actions


def dedupe(actions: list[CivilAction]) -> list[CivilAction]:
    """Satukan kegiatan yang sama yang dilaporkan lebih dari sekali.

    Rekap hari yang sama kerap diposting ulang pada hari berikutnya. Tanpa
    penyatuan ini satu rencana aksi terhitung beberapa kali, dan jumlah
    kegiatan maupun jumlah massa pada ringkasan menjadi berlipat.
    """
    seen: dict[tuple[str | None, ...], CivilAction] = {}
    for action in actions:
        key = (
            action.activity_date,
            action.time_start,
            (action.location or "").lower() or None,
            (action.organizer or "").lower() or None,
        )
        kept = seen.get(key)
        if kept is None:
            seen[key] = action
            continue
        # Pertahankan rekaman yang paling lengkap; laporan ulang kerap lebih rinci.
        if _filled(action) > _filled(kept):
            seen[key] = action
    return list(seen.values())


def _filled(action: CivilAction) -> int:
    return sum(
        1
        for value in (
            action.organizer,
            action.leader,
            action.crowd_reported,
            action.demand,
            action.region,
            action.area,
        )
        if value is not None
    )


def _actions_in(message: Message, result: Extraction) -> None:
    body = message.body
    if not (LABELED_ITEM.search(body) or NUMBERED_ITEM.search(body)):
        return

    header = body.strip().splitlines()[0] if body.strip() else ""
    activity_date = _header_date(header) or _header_date(body[:400])
    region = _header_region(header) or _header_region(body[:400])
    reported_on = message.sent.isoformat()

    result.actions.extend(_labeled_actions(body, activity_date, region, reported_on))
    _numbered_actions(body, activity_date, region, reported_on, result)


def _labeled_actions(
    body: str, activity_date: str | None, region: str | None, reported_on: str
) -> list[CivilAction]:
    kind_at = _kind_positions(body)
    out: list[CivilAction] = []

    for match in LABELED_ITEM.finditer(body):
        item = match.group(2).strip()
        if "Pukul" not in item:
            continue
        fields = _labeled_fields(item)
        if not fields:
            continue

        start, end = _times(item)
        crowd, crowd_issue = _crowd(fields.get("Jumlah"))

        action = CivilAction(
            activity_date=activity_date,
            region=region,
            area=None,
            time_start=start,
            time_end=end,
            location=_clean(fields.get("Tempat")),
            organizer=_clean(fields.get("Pelaksana")),
            leader=_clean(fields.get("Pimpinan")),
            crowd_reported=crowd,
            kind=_labeled_kind(fields, match.start(), kind_at),
            demand=_clean(fields.get("Tuntutan")),
            reported_on=reported_on,
            source_format="berlabel",
        )
        if crowd_issue:
            action.issues.append(crowd_issue)
        if action.location is None:
            action.issues.append("lokasi tidak tercantum pada laporan")
        out.append(action)

    return out


def _numbered_actions(
    body: str,
    activity_date: str | None,
    region: str | None,
    reported_on: str,
    result: Extraction,
) -> None:
    if ROMAN_SECTION.search(body):
        result.skipped.append(
            "laporan naratif berpenomoran Romawi dilewati: "
            f"{body.strip().splitlines()[0][:80] if body.strip() else ''}"
        )
        return
    headings = [
        (m.start(), m.group(1).strip())
        for m in KECAMATAN_HEADING.finditer(body)
        if not NOT_AN_AREA.match(m.group(1).strip())
    ]
    kind_at = _kind_positions(body)
    # Rekap kecamatan diawali judul "RENCANA KEGIATAN AKSI UNJUK RASA";
    # judul itu yang menetapkan jenis, bukan anggapan atas isi butir.
    header_kind: ActivityKind | None = (
        "unjuk_rasa" if UNRAS_WORDS.search(body[:300]) else None
    )
    lines = body.splitlines(keepends=True)

    starts: list[tuple[int, int]] = []  # (offset, index baris)
    offset = 0
    for index, line in enumerate(lines):
        if NUMBERED_ITEM.match(line):
            starts.append((offset, index))
        offset += len(line)

    for n, (item_offset, line_index) in enumerate(starts):
        stop = starts[n + 1][1] if n + 1 < len(starts) else len(lines)
        block = [ln.strip() for ln in lines[line_index:stop]]
        block = [ln for ln in block if ln and not KECAMATAN_HEADING.match(ln + "\n")]
        if not block:
            continue

        start, end = _times(block[0])
        head = re.sub(r"^\s*\d+\s*\.\s*Pukul[^,]*,\s*", "", block[0])
        # Sebagian butir menuliskan seluruh kegiatan pada satu baris, termasuk
        # penanggung jawab dan jumlah massa. Keduanya dikeluarkan lebih dahulu
        # agar tidak tertumpuk ke dalam kolom lokasi.
        head, inline_leader, inline_crowd, inline_issue = _split_inline(head)
        location = _clean(head)

        organizer: str | None = None
        leader: str | None = inline_leader
        crowd: int | None = inline_crowd
        crowd_issue: str | None = inline_issue if inline_crowd is None else None
        demand_parts: list[str] = []

        for line in block[1:]:
            pj = PJ_LINE.match(line)
            if pj and leader is None:
                leader = _clean(pj["name"])
                crowd, crowd_issue = _crowd(pj["crowd"])
                continue
            if line.startswith('"') or demand_parts:
                demand_parts.append(line)
                continue
            if organizer is None:
                organizer = _clean(line)

        action = CivilAction(
            activity_date=activity_date,
            region=region,
            area=_area_for(item_offset, headings),
            time_start=start,
            time_end=end,
            location=location,
            organizer=organizer,
            leader=leader,
            crowd_reported=crowd,
            kind=_kind_at(item_offset, kind_at)
            if _kind_at(item_offset, kind_at) != "tidak_ditentukan"
            else (header_kind or "tidak_ditentukan"),
            demand=_clean(" ".join(demand_parts).strip('"')) or None,
            reported_on=reported_on,
            source_format="bernomor",
        )
        # Nama pelaksana saja terlalu lemah sebagai syarat: baris berikutnya
        # pada daftar bernomor dapat terbaca sebagai pelaksana. Butir diterima
        # bila ada penanggung jawab, ada jumlah massa, atau butir berada di
        # bawah judul kecamatan yang memang menandai rekap wilayah.
        strong = (
            action.leader is not None
            or action.crowd_reported is not None
            or (action.area is not None and action.organizer is not None)
        )
        if not strong:
            result.skipped.append(
                f"baris bernomor tanpa keterangan kegiatan: {block[0][:80]}"
            )
            continue

        if crowd_issue:
            action.issues.append(crowd_issue)
        result.actions.append(action)


def _labeled_kind(
    fields: dict[str, str], offset: int, kind_at: list[tuple[int, ActivityKind]]
) -> ActivityKind:
    """Tentukan jenis kegiatan dari bukti yang ada pada butir itu sendiri.

    Urutan kepercayaan: bidang "Bentuk giat" yang menyebut jenis secara
    langsung, lalu keberadaan "Tuntutan". Butir unjuk rasa pada rekap ini
    selalu membawa tuntutan; konser, lomba lari, dan wisuda tidak pernah.

    Butir tanpa kedua bidang itu tidak dinyatakan unjuk rasa meskipun berada
    di bawah judul seksi Unras. Konser berkapasitas puluhan ribu yang salah
    terhitung sebagai massa aksi akan menggeser gambaran tekanan keamanan
    jauh melampaui apa yang dilaporkan.
    """
    from_form = kind_from_form(fields.get("Bentuk giat"))
    if from_form is not None:
        return from_form
    if fields.get("Tuntutan"):
        return "unjuk_rasa"
    section = _kind_at(offset, kind_at)
    return "tidak_ditentukan" if section == "unjuk_rasa" else section


def _labeled_fields(item: str) -> dict[str, str]:
    marks = list(LABEL_FIND.finditer(item))
    if not marks:
        return {}
    fields: dict[str, str] = {}
    for i, mark in enumerate(marks):
        label = mark.group(1).title().replace("Giat", "giat")
        stop = marks[i + 1].start() if i + 1 < len(marks) else len(item)
        fields[_canonical(label)] = item[mark.end() : stop].strip()
    return fields


def _canonical(label: str) -> str:
    low = label.lower()
    for known in LABELS:
        if known.lower() == low:
            return known
    return label


def _kind_positions(body: str) -> list[tuple[int, ActivityKind]]:
    marks: list[tuple[int, ActivityKind]] = []
    for m in SECTION_UNRAS.finditer(body):
        marks.append((m.start(), "unjuk_rasa"))
    for m in SECTION_GIAT.finditer(body):
        marks.append((m.start(), "giat_masyarakat"))
    for m in SECTION_POLRI.finditer(body):
        marks.append((m.start(), "giat_kepolisian"))
    marks.sort()
    return marks


def kind_from_form(bentuk_giat: str | None) -> ActivityKind | None:
    """Tentukan jenis dari bidang "Bentuk giat" bila laporan mencantumkannya."""
    if not bentuk_giat:
        return None
    return "unjuk_rasa" if UNRAS_WORDS.search(bentuk_giat) else "giat_masyarakat"


def _kind_at(offset: int, marks: list[tuple[int, ActivityKind]]) -> ActivityKind:
    kind: ActivityKind = "tidak_ditentukan"
    for position, value in marks:
        if position <= offset:
            kind = value
        else:
            break
    return kind


def _area_for(offset: int, headings: list[tuple[int, str]]) -> str | None:
    area = None
    for position, value in headings:
        if position <= offset:
            area = value
        else:
            break
    return area


def _times(text: str) -> tuple[str | None, str | None]:
    match = TIME_RANGE.search(text)
    if not match:
        return None, None
    start = f"{int(match.group(1)):02d}:{match.group(2)}"
    end = (
        f"{int(match.group(3)):02d}:{match.group(4)}"
        if match.group(3) is not None
        else None
    )
    return start, end


def _crowd(text: str | None) -> tuple[int | None, str | None]:
    if not text:
        return None, "jumlah massa tidak tercantum pada laporan"
    match = CROWD.search(text)
    if not match:
        return None, "jumlah massa tidak terbaca dari laporan"
    digits = match.group(1).replace(".", "").replace(",", "")
    if not digits.isdigit():
        return None, "jumlah massa tidak terbaca dari laporan"
    return int(digits), None


INLINE_PJ = re.compile(
    r"(?:Penanggung\s*jawab|P\.\s*Jawab|Pimpinan|\bp\.?\s?j\.?)\s*[:.]?\s*"
    r"([^,.()]{2,60})",
    re.IGNORECASE,
)
INLINE_CROWD = re.compile(
    r"(?:Jumlah(?:\s+Peserta)?\s*[:.]?\s*)?(?:±\s*|kl\.?\s*)?"
    r"([\d][\d.,]*)\s*(?:[Oo]rang|[Pp]eserta)\b"
)


def _split_inline(text: str) -> tuple[str, str | None, int | None, str | None]:
    """Keluarkan penanggung jawab dan jumlah massa dari baris kegiatan."""
    leader: str | None = None
    crowd: int | None = None
    issue: str | None = None

    pj = INLINE_PJ.search(text)
    if pj:
        leader = _clean(pj.group(1))
        text = text[: pj.start()]

    found = INLINE_CROWD.search(text)
    if found:
        crowd, issue = _crowd(found.group(0))
        text = text[: found.start()] + text[found.end() :]

    return text, leader, crowd, issue


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    text = unicodedata.normalize("NFKC", value)
    # Nomor telepon kerap menempel pada nama penanggung jawab. Nomor tidak
    # pernah disimpan, termasuk ketika penyertaan nama dipilih secara sadar.
    text = strip_phone_numbers(text)
    text = text.replace("*", " ")
    text = re.sub(r"\s+", " ", text).strip().strip(",").strip()
    # Titik penutup kalimat laporan tidak membawa makna pada nilai bidang.
    text = re.sub(r"\.+$", "", text).strip()
    return text or None


def _export_date(token: str) -> date | None:
    for fmt in ("%d/%m/%y", "%m/%d/%y"):
        try:
            return datetime.strptime(token, fmt).date()
        except ValueError:
            continue
    return None


def _header_date(text: str) -> str | None:
    match = HEADER_DATE.search(text)
    if not match:
        return None
    month = BULAN.get(match.group(2).lower())
    if month is None:
        return None
    try:
        return date(int(match.group(3)), month, int(match.group(1))).isoformat()
    except ValueError:
        return None


def canonical_region(text: str | None) -> str | None:
    """Petakan penyebutan wilayah ke kode zona Jabodetabek.

    Teks yang tidak cocok dengan satu alias pun mengembalikan ``None``.
    Wilayah tidak ditebak dari isi laporan.
    """
    if not text:
        return None
    low = unicodedata.normalize("NFKC", text).lower()
    for alias in _ALIAS_ORDER:
        if re.search(rf"\b{re.escape(alias)}\b", low):
            return REGION_ALIAS[alias]
    return None


def _header_region(text: str) -> str | None:
    return canonical_region(text)


def sender_token(sender: str) -> str:
    """Token stabil pengganti identitas pengirim.

    Nomor telepon tidak disimpan. Token memungkinkan penelusuran bahwa dua
    laporan berasal dari pengirim yang sama tanpa menyimpan identitasnya.
    """
    digest = hashlib.sha256(sender.strip().encode("utf-8")).hexdigest()
    return f"relay-{digest[:10]}"


def strip_phone_numbers(text: str) -> str:
    return PHONE.sub("[nomor disunting]", text)


# Relay grup WhatsApp meneruskan rekap yang asal-usulnya tidak diverifikasi
# penerbit. Tier C3 menyatakan itu apa adanya. Menaikkannya akan membuat
# pembaca memperlakukan rekap teruskan sebagai keterangan resmi.
RELAY_RELIABILITY = "C3"
RELAY_SOURCE_ID = "relay-wa-unras"


def digest(
    extraction: Extraction,
    *,
    publisher: str,
    include_pii: bool = False,
) -> dict[str, Any]:
    """Susun rekap kegiatan sipil dari hasil ekstraksi.

    Keluaran ini bukan SITREP. Tidak ada skor risiko di dalamnya, karena tidak
    ada analis yang menetapkannya. Yang ada hanyalah kegiatan sebagaimana
    dilaporkan, beserta hitungan atas laporan itu.
    """
    raw = extraction.actions
    unique = dedupe(raw)
    unique.sort(key=lambda a: (a.activity_date or "", a.time_start or "", a.region or ""))

    visible = unique if include_pii else [a.redacted() for a in unique]
    dates = sorted({a.activity_date for a in unique if a.activity_date})

    return {
        "generated_from": "whatsapp-export",
        "redacted": not include_pii,
        "window": {
            "from": dates[0] if dates else None,
            "to": dates[-1] if dates else None,
        },
        "source": {
            "id": RELAY_SOURCE_ID,
            "reliability": RELAY_RELIABILITY,
            "publisher": publisher,
        },
        "counts": {
            "actions": len(unique),
            "duplicates_merged": len(raw) - len(unique),
            "skipped_lines": len(extraction.skipped),
            "by_kind": _count_by_kind(unique),
            "without_crowd_figure": sum(1 for a in unique if a.crowd_reported is None),
        },
        "actions": [_action_json(a) for a in visible],
        "skipped": extraction.skipped,
    }


def _count_by_kind(actions: list[CivilAction]) -> dict[str, dict[str, int]]:
    """Hitung kegiatan dan massa terlapor per jenis.

    Dipisah per jenis dengan sengaja. Satu total gabungan akan mencampur
    massa konser dan massa aksi, dan angka itu tidak menjawab pertanyaan
    mana pun yang berguna.
    """
    out: dict[str, dict[str, int]] = {}
    for action in actions:
        row = out.setdefault(action.kind, {"actions": 0, "crowd_reported": 0})
        row["actions"] += 1
        if action.crowd_reported is not None:
            row["crowd_reported"] += action.crowd_reported
    return out


def _action_json(action: CivilAction) -> dict[str, Any]:
    payload = {
        "activity_date": action.activity_date,
        "region": action.region,
        "area": action.area,
        "time_start": action.time_start,
        "time_end": action.time_end,
        "location": action.location,
        "organizer": action.organizer,
        "crowd_reported": action.crowd_reported,
        "kind": action.kind,
        "demand": action.demand,
        "reported_on": action.reported_on,
        "source_format": action.source_format,
    }
    if action.leader is not None:
        payload["leader"] = action.leader
    if action.issues:
        payload["issues"] = list(action.issues)
    return payload


def sitrep_fragment(
    extraction: Extraction,
    edition_date: str,
    *,
    publisher: str,
    include_pii: bool = False,
) -> dict[str, Any]:
    """Bentuk potongan SITREP: alert, satu bagian isi, dan satu sumber.

    Potongan ini tidak memuat ``risk``. Skor pilar ditetapkan analis, bukan
    diturunkan dari jumlah massa yang dilaporkan.
    """
    edition = date.fromisoformat(edition_date)
    unique = dedupe(extraction.actions)
    upcoming = [
        a
        for a in unique
        if a.activity_date and date.fromisoformat(a.activity_date) >= edition
    ]
    upcoming.sort(key=lambda a: (a.activity_date or "", a.time_start or ""))

    visible = upcoming if include_pii else [a.redacted() for a in upcoming]

    alerts = [
        {
            "horizon": _horizon(edition, date.fromisoformat(a.activity_date or edition_date)),
            "headline": _headline(a),
            "detail": _detail(a),
            "claim_tag": "FACT",
            "source_ids": [RELAY_SOURCE_ID],
        }
        for a in visible
        if a.kind == "unjuk_rasa"
    ]

    claims = [
        {"text": _detail(a), "tag": "FACT", "source_ids": [RELAY_SOURCE_ID]}
        for a in visible
    ]
    if not claims:
        claims = [
            {
                "text": "Data belum tersedia. Tidak ada rencana kegiatan terlapor "
                f"pada relay untuk tanggal {edition_date} atau sesudahnya.",
                "tag": "FACT",
            }
        ]

    return {
        "alerts": alerts,
        "section": {
            "key": "civil_action_watch",
            "title": "Security — Civil Action Watch",
            "claims": claims,
        },
        "source": {
            "id": RELAY_SOURCE_ID,
            "reliability": RELAY_RELIABILITY,
            "publisher": publisher,
            "title": "Rekap rencana kegiatan unjuk rasa, diteruskan grup relay",
        },
    }


def _horizon(edition: date, activity: date) -> str:
    delta = (activity - edition).days
    if delta <= 0:
        return "0-24h"
    if delta == 1:
        return "0-72h"
    return "0-30d"


def _headline(action: CivilAction) -> str:
    where = action.location or "lokasi tidak tercantum"
    when = action.time_start or "jam tidak tercantum"
    return f"{when} WIB — {where}"


def _detail(action: CivilAction) -> str:
    """Rumuskan klaim sebagai laporan, bukan sebagai kepastian.

    Yang dapat dipastikan penerbit adalah adanya laporan, bukan terjadinya
    kegiatan. Kalimat disusun agar perbedaan itu tidak kabur saat dibaca.
    """
    parts = [
        "Relay melaporkan rencana",
        "unjuk rasa" if action.kind == "unjuk_rasa" else "giat masyarakat",
    ]
    if action.activity_date:
        parts.append(f"pada {action.activity_date}")
    if action.time_start:
        parts.append(f"pukul {action.time_start} WIB")
    if action.location:
        parts.append(f"di {action.location}")
    if action.organizer:
        parts.append(f"oleh {action.organizer}")

    sentence = " ".join(parts) + "."

    if action.crowd_reported is not None:
        sentence += f" Jumlah massa yang dilaporkan {action.crowd_reported} orang."
    else:
        sentence += " Jumlah massa: Data belum tersedia."

    if action.demand:
        sentence += f" Tuntutan: {action.demand}"
        if not sentence.endswith("."):
            sentence += "."

    return sentence
