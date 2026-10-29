"""Pembacaan arsip terbit menjadi indeks yang dikonsumsi dashboard.

Jalur produksi menuliskan dua berkas per edisi ke folder ``01_Daily Brief``:
DOCX bahasa Inggris dan TXT bahasa Indonesia untuk WhatsApp. Modul ini membaca
folder itu apa adanya, menurunkan identitas edisi dari nama berkas, dan
menyusun indeks urut menurun berdasarkan penghitung edisi.

Arsip adalah sumber kebenaran. Modul ini tidak menulis apa pun ke dalamnya.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

FILENAME = re.compile(
    r"^MJS-(?P<date>\d{4}-\d{2}-\d{2})-(?P<seq>\d{3})-(?P<variant>PREVIEW-EN|WA-ID)\."
    r"(?P<ext>docx|txt)$"
)

VARIANT_ROLE = {
    "PREVIEW-EN": "brief",
    "WA-ID": "whatsapp",
}


@dataclass
class EditionRecord:
    """Satu edisi beserta berkas yang ditemukan untuknya."""

    edition_id: str
    date: str
    sequence: int
    brief: str | None = None
    whatsapp: str | None = None
    issues: list[str] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return self.brief is not None and self.whatsapp is not None


def scan(directory: str | Path) -> list[EditionRecord]:
    """Baca satu folder arsip dan kembalikan daftar edisi, terbaru lebih dahulu."""
    root = Path(directory)
    if not root.is_dir():
        raise NotADirectoryError(f"folder arsip tidak ditemukan: {root}")

    records: dict[str, EditionRecord] = {}
    unparsed: list[str] = []

    for path in sorted(root.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        match = FILENAME.match(path.name)
        if not match:
            unparsed.append(path.name)
            continue

        date = match["date"]
        seq = int(match["seq"])
        edition_id = f"MJS-{date}-{match['seq']}"
        record = records.setdefault(
            edition_id,
            EditionRecord(edition_id=edition_id, date=date, sequence=seq),
        )

        role = VARIANT_ROLE[match["variant"]]
        existing = getattr(record, role)
        if existing is not None:
            # Dua berkas untuk peran yang sama pada satu edisi tidak digabung
            # secara diam-diam; konflik arsip harus terlihat.
            record.issues.append(
                f"berkas {role} ganda: {existing} dan {path.name}"
            )
        else:
            setattr(record, role, path.name)

    ordered = sorted(records.values(), key=lambda r: (r.sequence, r.date), reverse=True)

    _flag_sequence_collisions(ordered)
    for record in ordered:
        if not record.complete:
            missing = "brief DOCX" if record.brief is None else "versi WA TXT"
            record.issues.append(f"edisi tidak lengkap: {missing} belum ada")

    if unparsed:
        ordered.append(
            EditionRecord(
                edition_id="UNPARSED",
                date="",
                sequence=0,
                issues=[f"nama berkas di luar pola penomoran: {name}" for name in unparsed],
            )
        )

    return ordered


def next_sequence(records: list[EditionRecord]) -> int:
    """Penghitung edisi berikutnya: NNN tertinggi pada arsip ditambah satu."""
    real = [r.sequence for r in records if r.edition_id != "UNPARSED"]
    return (max(real) + 1) if real else 1


def _flag_sequence_collisions(records: list[EditionRecord]) -> None:
    by_sequence: dict[int, list[EditionRecord]] = {}
    for record in records:
        by_sequence.setdefault(record.sequence, []).append(record)
    for sequence, group in by_sequence.items():
        if len(group) > 1:
            ids = ", ".join(r.edition_id for r in group)
            for record in group:
                record.issues.append(
                    f"konflik penomoran: NNN={sequence:03d} dipakai oleh {ids}"
                )


def to_index(records: list[EditionRecord]) -> str:
    """Serialkan indeks arsip sebagai JSON untuk dibaca dashboard."""
    payload = {
        "generated_from": "archive.scan",
        "next_sequence": next_sequence(records),
        "editions": [asdict(r) for r in records],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
