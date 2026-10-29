"""Validasi doktrin atas SITREP yang sudah dinormalkan.

Skema JSON (``schema/sitrep.schema.json``) menjaga bentuk data. Modul ini
menjaga aturan yang tidak dapat dinyatakan dalam skema: integritas rujukan
sumber, konsistensi komposit terhadap pilar, larangan penyebutan, dan
kesesuaian klasifikasi terhadap tier.

Keluaran berupa daftar temuan, bukan pengecualian. Satu dokumen diperiksa
sampai selesai agar penyusun melihat seluruh masalah dalam satu lintasan,
bukan satu per satu.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from .msrm import (
    CLAIM_TAGS,
    HORIZONS,
    METHODOLOGY,
    PILLARS,
    RELIABILITY_TIERS,
    composite,
)

Severity = Literal["error", "warning"]

EDITION_ID = re.compile(r"^MJS-(\d{4})-(\d{2})-(\d{2})-(\d{3})$")

# Penyebutan firma intelijen dan konsultan asing dilarang pada produk apa pun.
_FORBIDDEN = (
    (re.compile(r"\bcontrol\s+risks\b", re.IGNORECASE), "Control Risks"),
    (re.compile(r"\bcrisis\s?24\b", re.IGNORECASE), "Crisis24"),
    (re.compile(r"\bdeloitte\b", re.IGNORECASE), "Deloitte"),
    (re.compile(r"\bpwc\b", re.IGNORECASE), "PwC"),
    (re.compile(r"\bpricewaterhousecoopers\b", re.IGNORECASE), "PricewaterhouseCoopers"),
    # EY hanya dicocokkan sebagai token huruf besar berdiri sendiri, agar kata
    # umum seperti "key" atau "they" tidak ikut tertangkap.
    (re.compile(r"\bEY\b"), "EY"),
    (re.compile(r"\bernst\s*&\s*young\b", re.IGNORECASE), "Ernst & Young"),
)

_EMOJI = re.compile(
    "["
    "\U0001f300-\U0001faff"
    "\U0001f000-\U0001f2ff"
    "☀-➿"
    "️"
    "]"
)

NO_DATA = "Data belum tersedia"


@dataclass(frozen=True)
class Finding:
    severity: Severity
    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.code} at {self.path}: {self.message}"


def validate(doc: dict[str, Any]) -> list[Finding]:
    """Periksa satu SITREP terhadap aturan doktrin MJ-Sentinel."""
    out: list[Finding] = []
    out += _check_edition(doc.get("edition", {}))
    out += _check_risk(doc.get("risk", {}))
    sources = doc.get("sources", [])
    source_ids = _collect_source_ids(sources)
    out += _check_sources(sources)
    out += _check_claims(doc, source_ids)
    out += _check_language(doc)
    return out


def _check_edition(edition: dict[str, Any]) -> list[Finding]:
    out: list[Finding] = []
    path = "edition"

    edition_id = edition.get("id", "")
    match = EDITION_ID.match(str(edition_id))
    if not match:
        out.append(
            Finding(
                "error",
                "EDITION_ID_FORMAT",
                f"{path}.id",
                f"harus MJS-YYYY-MM-DD-NNN, diterima {edition_id!r}",
            )
        )
    else:
        year, month, day, seq = match.groups()
        date = edition.get("date")
        if date and date != f"{year}-{month}-{day}":
            out.append(
                Finding(
                    "error",
                    "EDITION_DATE_MISMATCH",
                    f"{path}.date",
                    f"tanggal {date} tidak sesuai id edisi {edition_id}",
                )
            )
        sequence = edition.get("sequence")
        if isinstance(sequence, int) and int(seq) != sequence:
            out.append(
                Finding(
                    "error",
                    "EDITION_SEQUENCE_MISMATCH",
                    f"{path}.sequence",
                    f"sequence {sequence} tidak sesuai NNN={seq} pada id edisi",
                )
            )

    if edition.get("methodology") != METHODOLOGY:
        out.append(
            Finding(
                "error",
                "METHODOLOGY_LABEL",
                f"{path}.methodology",
                f"label metodologi wajib {METHODOLOGY!r}",
            )
        )

    classification = edition.get("classification")
    tier = edition.get("tier")
    if classification == "CLIENT_TIER_A" and tier != "A":
        out.append(
            Finding(
                "error",
                "CLASSIFICATION_TIER_MISMATCH",
                f"{path}.tier",
                "klasifikasi CLIENT_TIER_A menuntut tier A",
            )
        )
    if classification == "PREVIEW_OPEN_REDISTRIBUTION" and tier != "B":
        out.append(
            Finding(
                "error",
                "CLASSIFICATION_TIER_MISMATCH",
                f"{path}.tier",
                "klasifikasi PREVIEW menuntut tier B",
            )
        )
    if tier == "A":
        out.append(
            Finding(
                "warning",
                "TIER_A_NOT_ACTIVATED",
                f"{path}.tier",
                "Tier A belum berjalan; terbit hanya setelah protokol aktivasi klien diterima",
            )
        )
    return out


def _check_risk(risk: dict[str, Any]) -> list[Finding]:
    out: list[Finding] = []
    pillars = risk.get("pillars") or {}
    reported = risk.get("composite")

    if not all(isinstance(pillars.get(p), int) for p in PILLARS):
        return out  # bentuk data ditangani skema JSON

    try:
        expected = composite(dict(pillars))
    except (ValueError, TypeError) as exc:
        return [Finding("error", "COMPOSITE_UNCOMPUTABLE", "risk.pillars", str(exc))]

    if reported != expected.score:
        out.append(
            Finding(
                "error",
                "COMPOSITE_MISMATCH",
                "risk.composite",
                f"komposit terlapor {reported} tidak cocok dengan hasil hitung {expected.score} "
                f"atas pilar yang diberikan",
            )
        )
    if expected.was_floored:
        out.append(
            Finding(
                "warning",
                "COMPOSITE_FLOORED",
                "risk.composite",
                f"komposit diangkat ke ambang HIGH karena pilar {expected.floored_by} "
                f"berada pada band CRITICAL (rata-rata berbobot {expected.weighted_raw:.1f})",
            )
        )
    return out


def _collect_source_ids(sources: list[dict[str, Any]]) -> set[str]:
    return {str(s.get("id")) for s in sources if s.get("id")}


def _check_sources(sources: list[dict[str, Any]]) -> list[Finding]:
    out: list[Finding] = []
    seen: set[str] = set()
    for i, src in enumerate(sources):
        path = f"sources[{i}]"
        sid = str(src.get("id", ""))
        if sid in seen:
            out.append(Finding("error", "SOURCE_ID_DUPLICATE", path, f"id sumber ganda: {sid!r}"))
        seen.add(sid)
        tier = src.get("reliability")
        if tier not in RELIABILITY_TIERS:
            out.append(
                Finding(
                    "error",
                    "SOURCE_RELIABILITY_TIER",
                    f"{path}.reliability",
                    f"tier harus salah satu dari {', '.join(RELIABILITY_TIERS)}, diterima {tier!r}",
                )
            )
    return out


def _check_claims(doc: dict[str, Any], source_ids: set[str]) -> list[Finding]:
    out: list[Finding] = []

    for claim, path in _walk_claims(doc):
        tag = claim.get("tag")
        if tag not in CLAIM_TAGS:
            out.append(
                Finding(
                    "error",
                    "CLAIM_TAG_MISSING",
                    f"{path}.tag",
                    f"setiap klaim wajib bertanda {'/'.join(CLAIM_TAGS)}, diterima {tag!r}",
                )
            )
            continue

        refs = claim.get("source_ids") or []
        text = str(claim.get("text", ""))

        if tag == "FACT" and not refs and NO_DATA.lower() not in text.lower():
            out.append(
                Finding(
                    "error",
                    "FACT_WITHOUT_SOURCE",
                    path,
                    "klaim FACT wajib merujuk sekurang-kurangnya satu sumber",
                )
            )

        for ref in refs:
            if str(ref) not in source_ids:
                out.append(
                    Finding(
                        "error",
                        "SOURCE_REF_DANGLING",
                        path,
                        f"rujukan {ref!r} tidak ada pada Source Reliability Table",
                    )
                )

    for i, alert in enumerate(doc.get("alerts", [])):
        path = f"alerts[{i}]"
        if alert.get("horizon") not in HORIZONS:
            out.append(
                Finding(
                    "error",
                    "HORIZON_UNKNOWN",
                    f"{path}.horizon",
                    f"horizon harus salah satu dari {', '.join(HORIZONS)}",
                )
            )
        if alert.get("claim_tag") == "FACT" and not (alert.get("source_ids") or []):
            out.append(
                Finding(
                    "error",
                    "FACT_WITHOUT_SOURCE",
                    path,
                    "alert bertanda FACT wajib merujuk sumber",
                )
            )

    return out


def _walk_claims(doc: dict[str, Any]):
    for i, section in enumerate(doc.get("sections", [])):
        for j, claim in enumerate(section.get("claims", [])):
            yield claim, f"sections[{i}].claims[{j}]"
    for i, entry in enumerate(doc.get("outlook", [])):
        claim = entry.get("claim")
        if isinstance(claim, dict):
            yield claim, f"outlook[{i}].claim"


def _check_language(doc: dict[str, Any]) -> list[Finding]:
    out: list[Finding] = []
    for text, path in _walk_text(doc):
        for pattern, label in _FORBIDDEN:
            if pattern.search(text):
                out.append(
                    Finding(
                        "error",
                        "FORBIDDEN_MENTION",
                        path,
                        f"penyebutan {label} dilarang pada produk MJ-Sentinel",
                    )
                )
        if _EMOJI.search(text):
            out.append(
                Finding("error", "EMOJI_PRESENT", path, "emoji dan ikon dekoratif dilarang")
            )
    return out


def _walk_text(node: Any, path: str = "$"):
    if isinstance(node, str):
        yield node, path
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from _walk_text(value, f"{path}.{key}" if path != "$" else key)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _walk_text(value, f"{path}[{i}]")


def errors(findings: list[Finding]) -> list[Finding]:
    return [f for f in findings if f.severity == "error"]


def passed(findings: list[Finding]) -> bool:
    return not errors(findings)
