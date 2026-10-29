"""Tes pola berulang. Nilai contoh bersifat struktural."""

from mjs_ingest.patterns import (
    by_date,
    by_hour,
    by_weekday,
    concurrency,
    recurring_organizers,
)

ACTIONS = [
    {
        "activity_date": "2026-10-19",
        "time_start": "13:00",
        "location": "Gd. Contoh A",
        "organizer": "Organisasi Contoh A",
        "crowd_reported": 20,
    },
    {
        "activity_date": "2026-10-19",
        "time_start": "13:00",
        "location": "Kantor Gd. Contoh A",
        "organizer": "Organisasi Contoh B",
        "crowd_reported": 30,
    },
    {
        "activity_date": "2026-10-20",
        "time_start": "10:00",
        "location": "Gd. Contoh B",
        "organizer": "Organisasi Contoh A",
        "crowd_reported": 15,
    },
]


def test_by_date_totals_actions_and_crowd():
    rows = by_date(ACTIONS)
    assert rows[0] == {
        "date": "2026-10-19",
        "actions": 2,
        "crowd_reported": 50,
        "weekday": "Senin",
    }


def test_by_date_skips_entries_without_a_date():
    assert by_date([{"activity_date": None, "time_start": "10:00"}]) == []


def test_by_hour_buckets_to_whole_hours():
    assert by_hour(ACTIONS) == [
        {"hour": 10, "actions": 1},
        {"hour": 13, "actions": 2},
    ]


def test_by_hour_ignores_unreadable_times():
    assert by_hour([{"time_start": None}, {"time_start": "pagi"}]) == []


def test_by_weekday_reports_how_many_days_it_counted():
    rows = by_weekday(ACTIONS)
    senin = next(r for r in rows if r["weekday"] == "Senin")
    assert senin == {"weekday": "Senin", "actions": 2, "days_observed": 1}


def test_recurring_organizers_needs_more_than_one_day():
    rows = recurring_organizers(ACTIONS)
    assert [r["organizer"] for r in rows] == ["Organisasi Contoh A"]
    assert rows[0]["days"] == 2


def test_concurrency_groups_same_point_and_hour():
    rows = concurrency(ACTIONS, {"contoh a": "Contoh A"})
    assert len(rows) == 1
    assert rows[0].groups == 2
    assert rows[0].crowd_reported == 50
    assert rows[0].label == "Contoh A"
    assert rows[0].organizers == ["Organisasi Contoh A", "Organisasi Contoh B"]


def test_concurrency_ignores_a_lone_group():
    single = [ACTIONS[2]]
    assert concurrency(single, {}) == []


def test_concurrency_matches_points_written_differently():
    # "Gd. Contoh A" dan "Kantor Gd. Contoh A" adalah satu titik.
    assert concurrency(ACTIONS, {})[0].point_key == "contoh a"
