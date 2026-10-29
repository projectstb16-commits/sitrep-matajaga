"""Tes deteksi laporan lapangan dan pemetaannya terhadap rencana.

Nilai contoh pada berkas ini bersifat struktural, bukan keterangan nyata.
"""

from mjs_ingest.incidents import (
    detect_reports,
    match_plans,
    observation_summary,
)
from mjs_ingest.whatsapp import parse_messages

POINTS = {"contoh a", "contoh b"}

FIELD = """20/10/26 18.40 - Pelapor Contoh: Izin, Pukul 18.35 WIB massa aksi di Gd. Contoh A sudah membubarkan diri.
- Akses Jl. Contoh Satu sudah di buka.
- Sitkon aman.
"""

PLAN = """19/10/26 07.00 - Pelapor Contoh: *Rengiat wil Jakarta Pusat 19 Oktober 2026 :*

*1.* Pukul 13.00 WIB, Tempat Gd. Contoh A, Pelaksana Organisasi Contoh A, Jumlah ± 20 orang, Tuntutan Tuntutan contoh.
"""

CHATTER = """21/10/26 09.00 - Pelapor Contoh: Selamat pagi, mohon info rengiat hari ini.
"""


def reports_of(text, points=POINTS):
    return detect_reports(parse_messages(text), points)


def test_field_report_is_detected():
    assert len(reports_of(FIELD)) == 1


def test_field_report_reads_time_signals_point_and_roads():
    report = reports_of(FIELD)[0]
    assert report.reported_on == "2026-10-20"
    assert report.reported_time == "18:35"
    assert "massa_bubar" in report.signals
    assert "akses_dibuka" in report.signals
    assert "situasi_aman" in report.signals
    assert report.point_keys == ["contoh a"]
    assert report.roads == ["Contoh Satu"]


def test_field_report_flags_traffic_effect():
    assert reports_of(FIELD)[0].affects_traffic is True


def test_plan_recap_is_not_treated_as_a_field_report():
    assert reports_of(PLAN) == []


def test_ordinary_chatter_is_not_a_field_report():
    assert reports_of(CHATTER) == []


def test_point_is_matched_only_against_known_points():
    assert reports_of(FIELD, points={"contoh b"})[0].point_keys == []


def test_narrative_spelling_is_normalised_before_matching():
    text = """20/10/26 18.40 - Pelapor Contoh: Massa di Kemen ESDM sudah membubarkan diri, situasi aman.
"""
    assert reports_of(text, points={"kementerian esdm"})[0].point_keys == [
        "kementerian esdm"
    ]


def test_sender_identity_is_replaced_by_a_token():
    report = reports_of(FIELD)[0]
    assert report.sender_token.startswith("relay-")
    assert "Pelapor" not in report.sender_token


def test_phone_numbers_are_removed_from_the_excerpt():
    text = """20/10/26 18.40 - Pelapor Contoh: Massa membubarkan diri, situasi aman. Kontak 0812-0000-0000.
"""
    assert "0812" not in reports_of(text)[0].excerpt


def test_match_links_plan_to_a_report_on_the_same_date_and_point():
    plans = [
        {
            "activity_date": "2026-10-20",
            "time_start": "13:00",
            "location": "Gd. Contoh A",
            "organizer": "Organisasi Contoh A",
        }
    ]
    matches = match_plans(plans, reports_of(FIELD))
    assert matches[0].observed is True
    assert matches[0].point_key == "contoh a"


def test_match_does_not_link_across_different_dates():
    plans = [{"activity_date": "2026-10-19", "location": "Gd. Contoh A"}]
    assert match_plans(plans, reports_of(FIELD))[0].observed is False


def test_match_does_not_link_different_points():
    plans = [{"activity_date": "2026-10-20", "location": "Gd. Contoh B"}]
    assert match_plans(plans, reports_of(FIELD))[0].observed is False


def test_summary_counts_reports_not_realisation():
    plans = [
        {"activity_date": "2026-10-20", "location": "Gd. Contoh A"},
        {"activity_date": "2026-10-20", "location": "Gd. Contoh B"},
    ]
    summary = observation_summary(match_plans(plans, reports_of(FIELD)))
    assert summary["plans"] == 2
    assert summary["plans_with_field_report"] == 1
    assert summary["plans_without_field_report"] == 1
    # Istilah "realisasi" tidak dipakai: ketiadaan laporan bukan bukti batal.
    assert "bukan bukti" in summary["note"]
    assert not any("realisasi" in key for key in summary)


def test_road_name_stops_before_the_rest_of_the_sentence():
    text = """20/10/26 18.40 - Pelapor Contoh: Massa membubarkan diri, Jl. Contoh Satu sudah di buka.
"""
    assert reports_of(text)[0].roads == ["Contoh Satu"]


def test_road_name_keeps_a_lowercase_part_of_the_name():
    text = """20/10/26 18.40 - Pelapor Contoh: Massa membubarkan diri di Jl. Imam bonjol, situasi aman.
"""
    assert reports_of(text)[0].roads == ["Imam bonjol"]


def test_direction_words_are_trimmed_from_road_names():
    text = """20/10/26 18.40 - Pelapor Contoh: Akses Jl. Contoh Satu Dari sudah di buka, aman terkendali.
"""
    assert reports_of(text)[0].roads == ["Contoh Satu"]
