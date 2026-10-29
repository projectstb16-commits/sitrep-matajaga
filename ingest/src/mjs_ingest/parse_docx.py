"""Ekstraksi SITREP dari DOCX terbit menjadi struktur sesuai skema.

Dokumen terbit menandai setiap klaim secara inline dengan ``[FACT]``,
``[ANALYSIS]``, atau ``[ASSUMPTION]``. Penanda itulah yang dipakai sebagai
batas klaim, bukan pemecahan per kalimat, sehingga satu klaim bertanda tetap
utuh walau terdiri atas beberapa kalimat.

Lingkup modul ini sengaja dibatasi pada teks paragraf dan heading. Angka pilar
risiko dalam dokumen terbit berada di dalam tabel Risk Dashboard dan belum
diekstraksi di sini; nilainya disuplai dari jalur produksi. Mengarang angka
dari dokumen yang belum terbaca akan melanggar aturan anti-halusinasi, jadi
bagian itu dibiarkan kosong secara eksplisit sampai ekstraktor tabel ditulis.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .archive import FILENAME

CLAIM_MARK = re.compile(r"\[(FACT|ANALYSIS|ASSUMPTION)\]\s*")


class DocxSupportMissing(RuntimeError):
    """python-docx belum terpasang."""


def parse(path: str | Path) -> dict[str, Any]:
    """Baca satu DOCX terbit dan kembalikan SITREP yang belum lengkap.

    Hasilnya belum tentu lolos ``validate``: bagian yang tidak dapat dibaca
    dari dokumen dibiarkan kosong agar kekurangannya muncul sebagai temuan,
    bukan tertutup oleh nilai bawaan yang tidak berdasar.
    """
    document = _open(path)
    source = Path(path)

    edition = _edition_from_filename(source.name)
    sections = _sections(document)

    return {
        "edition": edition,
        "risk": {},
        "zones": [],
        "alerts": [],
        "sections": sections,
        "sources": [],
    }


def _open(path: str | Path):
    try:
        import docx  # noqa: PLC0415 — impor ditunda agar paket inti tetap stdlib
    except ModuleNotFoundError as exc:  # pragma: no cover - bergantung lingkungan
        raise DocxSupportMissing(
            "pembacaan DOCX memerlukan python-docx. Pasang ekstra dokumen: "
            "pip install -e 'ingest[docx]'"
        ) from exc
    return docx.Document(str(path))


def _edition_from_filename(name: str) -> dict[str, Any]:
    match = FILENAME.match(name)
    if not match:
        raise ValueError(
            f"nama berkas di luar pola penomoran MJS-YYYY-MM-DD-NNN-VARIANT: {name}"
        )
    seq = match["seq"]
    return {
        "id": f"MJS-{match['date']}-{seq}",
        "date": match["date"],
        "sequence": int(seq),
        "classification": "PREVIEW_OPEN_REDISTRIBUTION",
        "tier": "B",
        "theatre_primary": "JABODETABEK",
        "methodology": "MSRM v1.1",
    }


def _sections(document) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue

        if _is_heading(paragraph):
            current = {"key": _slug(text), "title": text, "claims": []}
            sections.append(current)
            continue

        if current is None:
            # Teks sebelum heading pertama adalah blok cover; bukan isi bagian.
            continue

        current["claims"].extend(_claims(text))

    return sections


def _is_heading(paragraph) -> bool:
    style = (getattr(paragraph.style, "name", "") or "").lower()
    return style.startswith("heading") or style == "title"


def _claims(text: str) -> list[dict[str, Any]]:
    """Pecah satu paragraf pada penanda tag inline."""
    marks = list(CLAIM_MARK.finditer(text))
    if not marks:
        # Paragraf tanpa penanda tetap dibawa masuk tanpa tag, agar validator
        # melaporkannya sebagai CLAIM_TAG_MISSING alih-alih menghilang diam-diam.
        return [{"text": text}]

    claims: list[dict[str, Any]] = []
    for i, mark in enumerate(marks):
        start = mark.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[start:end].strip()
        if body:
            claims.append({"text": body, "tag": mark.group(1)})
    return claims


def _slug(title: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return cleaned or "section"
