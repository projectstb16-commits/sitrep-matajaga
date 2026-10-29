"""Perangkaian satu berkas analisis untuk dashboard.

Berkas ini menyatukan empat hal yang masing-masing dihitung modul tersendiri:
rekap kegiatan, peringkat titik, pola berulang, dan laporan lapangan beserta
pemetaannya terhadap rencana.

Yang tidak ada di sini, dan tidak boleh ditambahkan: skor risiko. Seluruh isi
berkas adalah hitungan atas laporan. Penilaian ditetapkan analis.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from . import patterns
from .incidents import detect_reports, match_plans, observation_summary
from .places import Place, coverage, rank_points
from .whatsapp import Extraction, Message, dedupe, digest


def build(
    extraction: Extraction,
    messages: list[Message],
    gazetteer: dict[str, Place],
    *,
    publisher: str,
    include_pii: bool = False,
) -> dict[str, Any]:
    """Susun berkas analisis lengkap."""
    base = digest(extraction, publisher=publisher, include_pii=include_pii)

    unique = dedupe(extraction.actions)
    plans = [
        a
        for a in base["actions"]
        if a.get("kind") == "unjuk_rasa"
    ]

    points = rank_points(plans, gazetteer)
    labels = {p.key: p.label for p in points}

    reports = detect_reports(messages, {p.key for p in points})
    matches = match_plans(plans, reports)

    return {
        **base,
        "points": {
            "coverage": coverage(points),
            "ranked": [asdict(p) for p in points],
        },
        "patterns": {
            "by_date": patterns.by_date(plans),
            "by_hour": patterns.by_hour(plans),
            "by_weekday": patterns.by_weekday(plans),
            "recurring_organizers": patterns.recurring_organizers(plans),
            "concurrency": [asdict(c) for c in patterns.concurrency(plans, labels)],
        },
        "field_reports": {
            "observation": observation_summary(matches),
            "reports": [asdict(r) for r in reports],
            "matched_plans": [
                {
                    "activity_date": m.plan.get("activity_date"),
                    "time_start": m.plan.get("time_start"),
                    "location": m.plan.get("location"),
                    "organizer": m.plan.get("organizer"),
                    "point_key": m.point_key,
                    "report_count": len(m.reports),
                    "signals": sorted({s for r in m.reports for s in r.signals}),
                }
                for m in matches
                if m.observed
            ],
        },
        "totals": {
            "messages": len(messages),
            "actions_all_kinds": len(unique),
            "plans_analysed": len(plans),
        },
    }
