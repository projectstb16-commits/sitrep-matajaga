"""Tes kanonikalisasi titik dan gazetteer.

Nilai contoh pada berkas ini ditulis sebagai penempatan struktural, bukan
keterangan nyata.
"""

import json

import pytest

from mjs_ingest.places import (
    Place,
    canonical_point,
    coverage,
    gazetteer_json,
    label_for,
    load_gazetteer,
    merge_gazetteer,
    rank_points,
)


@pytest.mark.parametrize(
    "written",
    [
        "Depan KPK RI Jl. Kuningan Persada Jaksel",
        "Kantor KPK RI",
        "KPK RI",
        "  depan   kpk ri  ",
    ],
)
def test_one_point_written_many_ways_gives_one_key(written):
    assert canonical_point(written) == "kpk ri"


def test_street_name_does_not_split_a_point():
    a = canonical_point("Kementerian Contoh Jl. Satu")
    b = canonical_point("Kementerian Contoh Jl. Dua")
    assert a == b


def test_first_place_in_a_combined_location_is_the_starting_point():
    assert canonical_point("Depan Gd. Contoh A & Depan Gd. Contoh B") == "contoh a"


def test_region_suffix_is_not_part_of_the_key():
    assert canonical_point("Gd. Contoh Jaksel") == canonical_point("Gd. Contoh")


def test_empty_location_has_no_key():
    assert canonical_point(None) is None
    assert canonical_point("   ") is None


def test_acronyms_are_capitalised_in_labels():
    assert label_for("kpk ri") == "KPK RI"
    assert label_for("kedubes rrt") == "Kedubes RRT"
    assert label_for("kementerian esdm") == "Kementerian ESDM"


def test_rank_orders_by_number_of_actions():
    actions = [
        {"location": "Gd. Contoh A", "activity_date": "2026-10-19", "crowd_reported": 10},
        {"location": "Kantor Gd. Contoh A", "activity_date": "2026-10-20", "crowd_reported": 20},
        {"location": "Gd. Contoh B", "activity_date": "2026-10-19", "crowd_reported": 5},
    ]
    ranked = rank_points(actions, {})
    assert ranked[0].actions == 2
    assert ranked[0].crowd_reported == 30
    assert ranked[0].recurring is True
    assert ranked[1].recurring is False


def test_point_without_coordinates_is_still_ranked():
    ranked = rank_points([{"location": "Gd. Contoh A", "activity_date": "2026-10-19"}], {})
    assert ranked[0].located is False
    assert ranked[0].lat is None


def test_gazetteer_coordinates_reach_the_ranking(tmp_path):
    file = tmp_path / "gazetteer.json"
    file.write_text(
        gazetteer_json(
            [
                Place(
                    key="contoh a",
                    label="Contoh A",
                    lat=-6.0,
                    lon=106.0,
                    source="Sumber contoh",
                )
            ]
        ),
        encoding="utf-8",
    )
    gaz = load_gazetteer(file)
    ranked = rank_points([{"location": "Gd. Contoh A", "activity_date": "2026-10-19"}], gaz)
    assert ranked[0].located is True
    assert (ranked[0].lat, ranked[0].lon) == (-6.0, 106.0)


def test_missing_gazetteer_file_is_not_an_error(tmp_path):
    assert load_gazetteer(tmp_path / "belum-ada.json") == {}


def test_merge_never_overwrites_coordinates_already_entered():
    existing = {
        "contoh a": Place(
            key="contoh a", label="Contoh A", lat=-6.0, lon=106.0, source="Sumber contoh"
        )
    }
    ranked = rank_points(
        [
            {"location": "Gd. Contoh A", "activity_date": "2026-10-19"},
            {"location": "Gd. Contoh B", "activity_date": "2026-10-19"},
        ],
        existing,
    )
    merged, added = merge_gazetteer(existing, ranked)
    kept = next(p for p in merged if p.key == "contoh a")
    assert (kept.lat, kept.lon) == (-6.0, 106.0)
    assert added == 1


def test_new_gazetteer_entry_starts_without_coordinates():
    merged, _ = merge_gazetteer({}, rank_points([{"location": "Gd. Contoh C"}], {}))
    assert merged[0].lat is None and merged[0].source is None


def test_gazetteer_json_round_trips():
    payload = json.loads(gazetteer_json([Place(key="contoh a", label="Contoh A")]))
    assert payload["places"][0]["key"] == "contoh a"
    assert payload["places"][0]["lat"] is None


def test_coverage_counts_actions_that_can_be_mapped():
    gaz = {
        "contoh a": Place(
            key="contoh a", label="Contoh A", lat=-6.0, lon=106.0, source="Sumber contoh"
        )
    }
    ranked = rank_points(
        [
            {"location": "Gd. Contoh A", "activity_date": "2026-10-19"},
            {"location": "Gd. Contoh A", "activity_date": "2026-10-20"},
            {"location": "Gd. Contoh B", "activity_date": "2026-10-19"},
        ],
        gaz,
    )
    assert coverage(ranked) == {
        "points": 2,
        "points_located": 1,
        "actions": 3,
        "actions_located": 2,
    }
