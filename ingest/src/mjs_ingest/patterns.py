"""Pola berulang pada rekap rencana kegiatan.

Seluruh keluaran modul ini adalah hitungan atas data yang ada: berapa kegiatan
pada suatu hari, pada jam berapa paling banyak dimulai, titik mana yang
berulang, dan di titik mana beberapa kelompok datang pada jam yang sama.

Tidak ada peramalan di sini. Hitungan masa lalu tidak diproyeksikan menjadi
perkiraan hari berikutnya; proyeksi adalah pekerjaan analis dan tunduk pada
batas outlook H+2.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any

HARI = (
    "Senin",
    "Selasa",
    "Rabu",
    "Kamis",
    "Jumat",
    "Sabtu",
    "Minggu",
)


@dataclass
class Concurrency:
    """Beberapa kelompok pada satu titik dan jam yang sama.

    Penumpukan seperti ini yang paling berpengaruh pada arus lalu lintas:
    tiga kelompok masing-masing 20 orang pada satu titik pukul 13.00 bukan
    tiga peristiwa kecil yang terpisah.
    """

    activity_date: str
    time_start: str
    point_key: str
    label: str
    groups: int
    crowd_reported: int
    organizers: list[str]


def by_date(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Jumlah kegiatan dan massa terlapor per tanggal."""
    bucket: dict[str, dict[str, int]] = defaultdict(
        lambda: {"actions": 0, "crowd_reported": 0}
    )
    for action in actions:
        day = action.get("activity_date")
        if not day:
            continue
        bucket[str(day)]["actions"] += 1
        crowd = action.get("crowd_reported")
        if isinstance(crowd, int):
            bucket[str(day)]["crowd_reported"] += crowd
    return [
        {"date": day, **values, "weekday": _weekday(day)}
        for day, values in sorted(bucket.items())
    ]


def by_hour(actions: list[dict[str, Any]]) -> list[dict[str, int]]:
    """Sebaran jam mulai, dalam jam bulat."""
    counter: Counter[int] = Counter()
    for action in actions:
        start = action.get("time_start")
        if not isinstance(start, str) or ":" not in start:
            continue
        try:
            counter[int(start.split(":")[0])] += 1
        except ValueError:
            continue
    return [{"hour": hour, "actions": counter[hour]} for hour in sorted(counter)]


def by_weekday(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sebaran menurut hari dalam pekan.

    Rentang data yang pendek membuat angka ini mudah disalahbaca sebagai
    kecenderungan. Jumlah hari yang teramati per nama hari ikut dilaporkan
    agar pembaca melihat dasar hitungannya.
    """
    actions_per: Counter[str] = Counter()
    days_seen: dict[str, set[str]] = defaultdict(set)
    for action in actions:
        day = action.get("activity_date")
        if not day:
            continue
        name = _weekday(str(day))
        if name is None:
            continue
        actions_per[name] += 1
        days_seen[name].add(str(day))
    return [
        {
            "weekday": name,
            "actions": actions_per[name],
            "days_observed": len(days_seen[name]),
        }
        for name in HARI
        if actions_per[name]
    ]


def recurring_organizers(
    actions: list[dict[str, Any]], minimum_days: int = 2
) -> list[dict[str, Any]]:
    """Pelaksana yang muncul pada lebih dari satu hari."""
    days: dict[str, set[str]] = defaultdict(set)
    counts: Counter[str] = Counter()
    for action in actions:
        organizer = action.get("organizer")
        day = action.get("activity_date")
        if not organizer or not day:
            continue
        days[organizer].add(str(day))
        counts[organizer] += 1

    rows = [
        {"organizer": name, "actions": counts[name], "days": len(seen)}
        for name, seen in days.items()
        if len(seen) >= minimum_days
    ]
    return sorted(rows, key=lambda r: (-r["days"], -r["actions"], r["organizer"]))


def concurrency(
    actions: list[dict[str, Any]], labels: dict[str, str], minimum_groups: int = 2
) -> list[Concurrency]:
    """Titik dengan beberapa kelompok pada tanggal dan jam yang sama."""
    from .places import canonical_point

    bucket: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for action in actions:
        day = action.get("activity_date")
        start = action.get("time_start")
        key = canonical_point(action.get("location"))
        if not (day and start and key):
            continue
        bucket[(str(day), str(start), key)].append(action)

    out: list[Concurrency] = []
    for (day, start, key), group in bucket.items():
        if len(group) < minimum_groups:
            continue
        out.append(
            Concurrency(
                activity_date=day,
                time_start=start,
                point_key=key,
                label=labels.get(key, key),
                groups=len(group),
                crowd_reported=sum(
                    a["crowd_reported"]
                    for a in group
                    if isinstance(a.get("crowd_reported"), int)
                ),
                organizers=sorted(
                    {a["organizer"] for a in group if a.get("organizer")}
                ),
            )
        )
    return sorted(
        out, key=lambda c: (-c.groups, -c.crowd_reported, c.activity_date, c.time_start)
    )


def _weekday(day: str) -> str | None:
    try:
        return HARI[date.fromisoformat(day).weekday()]
    except ValueError:
        return None
