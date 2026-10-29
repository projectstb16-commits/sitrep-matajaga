"""Tes parser rekap rengiat.

Seluruh isi contoh pada berkas ini adalah penempatan struktural: nama
organisasi, nama orang, dan lokasi sengaja ditulis sebagai "Contoh" agar tidak
dapat dikelirukan sebagai keterangan nyata. Yang diuji adalah bentuk data,
bukan muatannya.
"""

import pytest

from mjs_ingest.whatsapp import (
    canonical_region,
    dedupe,
    digest,
    extract,
    kind_from_form,
    parse_messages,
    sender_token,
    sitrep_fragment,
    strip_phone_numbers,
)

LABELED = """18/10/26 21.25 - Pelapor Contoh: *Rengiat Unras dan masyarakat wil Jakarta Selatan 19 Oktober 2026 :*

*Unras :*

*1.* Pukul 13.00 WIB, Tempat Lokasi Contoh Satu, Pelaksana Organisasi Contoh A, Pimpinan Nama Contoh A, Jumlah ± 100 Orang, Bentuk giat Unjuk rasa, Tuntutan Tuntutan contoh pertama.

*2.* Pukul 10.00 - 12.00 WIB, Tempat Lokasi Contoh Dua, Pelaksana Organisasi Contoh B, Pimpinan Nama Contoh B, Jumlah ± 15 orang, Bentuk giat Unjuk rasa, Tuntutan Tuntutan contoh kedua.

*Giat masyarakat :*

*3.* Pukul 08.00 - 18.00 WIB, Tempat Lokasi Contoh Tiga, Pelaksana Organisasi Contoh C, Bentuk giat Pertunjukan Seni, Pimpinan Nama Contoh C, Jumlah ± 2.000 Orang.
"""

NUMBERED = """19/10/26 07.00 - Pelapor Contoh: Rencana Kegiatan di Wilayah Jakarta Pusat. Hari Senin tanggal 19 Oktober 2026. Sbb :

*RENCANA KEGIATAN AKSI UNJUK RASA* :

*GAMBIR* :

1.Pukul 13.00 WIB, Lokasi Contoh Empat
Organisasi Contoh D.
Pj. Nama Contoh D, kl. 15 orang.
"Tuntutan contoh ketiga."

2.Pukul 14.00 WIB, Lokasi Contoh Lima
Organisasi Contoh E.
Pj. Nama Contoh E, kl. 20 orang.
"Tuntutan contoh keempat."
"""

NARRATIVE = """20/10/26 09.00 - Pelapor Contoh: PERIHAL : KEGIATAN CONTOH

*I. WAKTU :*
1. Hari : Selasa, 20 Oktober 2026
2. Pukul : 09.00 WIB s/d 11.40 WIB
3. Tempat : Lokasi Contoh Enam

*II. HADIR :*
1. Pejabat Contoh.
"""


def actions_of(text):
    return extract(parse_messages(text)).actions


def test_parse_messages_reads_date_and_sender():
    messages = parse_messages(LABELED)
    assert len(messages) == 1
    assert messages[0].sent.isoformat() == "2026-10-18"
    assert messages[0].sender == "Pelapor Contoh"


def test_labeled_format_reads_every_field():
    first = actions_of(LABELED)[0]
    assert first.activity_date == "2026-10-19"
    assert first.region == "JAKSEL"
    assert first.time_start == "13:00"
    assert first.location == "Lokasi Contoh Satu"
    assert first.organizer == "Organisasi Contoh A"
    assert first.leader == "Nama Contoh A"
    assert first.crowd_reported == 100
    assert first.kind == "unjuk_rasa"
    assert first.demand == "Tuntutan contoh pertama"


def test_time_range_keeps_both_ends():
    second = actions_of(LABELED)[1]
    assert (second.time_start, second.time_end) == ("10:00", "12:00")


def test_label_order_does_not_matter():
    # Pada butir giat masyarakat, "Bentuk giat" mendahului "Pimpinan".
    third = actions_of(LABELED)[2]
    assert third.organizer == "Organisasi Contoh C"
    assert third.leader == "Nama Contoh C"
    assert third.kind == "giat_masyarakat"


def test_thousand_separator_is_read_as_one_number():
    assert actions_of(LABELED)[2].crowd_reported == 2000


def test_numbered_format_reads_area_and_fields():
    actions = actions_of(NUMBERED)
    assert len(actions) == 2
    first = actions[0]
    assert first.region == "JAKPUS"
    assert first.area == "GAMBIR"
    assert first.organizer == "Organisasi Contoh D"
    assert first.leader == "Nama Contoh D"
    assert first.crowd_reported == 15
    assert first.demand == "Tuntutan contoh ketiga"
    assert first.source_format == "bernomor"


def test_section_title_is_not_mistaken_for_an_area():
    assert all(a.area != "RENCANA KEGIATAN AKSI UNJUK RASA" for a in actions_of(NUMBERED))


def test_narrative_report_yields_no_actions():
    result = extract(parse_messages(NARRATIVE))
    assert result.actions == []
    assert any("naratif" in s for s in result.skipped)


def test_item_without_demand_or_form_is_not_called_a_demonstration():
    # Konser berkapasitas besar di bawah judul Unras: jenis tidak dinyatakan.
    text = """18/10/26 21.25 - Pelapor Contoh: *Rengiat Unras wil Jakarta Pusat 19 Oktober 2026 :*

*Unras :*

*1.* Pukul 12.00 WIB, Tempat Lokasi Contoh Tujuh, Pelaksana Organisasi Contoh F, Pimpinan Nama Contoh F, Jumlah ± 50.000 orang.
"""
    action = actions_of(text)[0]
    assert action.crowd_reported == 50000
    assert action.kind == "tidak_ditentukan"


def test_demand_alone_is_enough_to_mark_a_demonstration():
    text = """18/10/26 21.25 - Pelapor Contoh: *Rengiat wil Jakarta Pusat 19 Oktober 2026 :*

*1.* Pukul 12.00 WIB, Tempat Lokasi Contoh Delapan, Pelaksana Organisasi Contoh G, Jumlah ± 20 orang, Tuntutan Tuntutan contoh kelima.
"""
    assert actions_of(text)[0].kind == "unjuk_rasa"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("wil Jaksel", "JAKSEL"),
        ("Wilayah Jakarta Selatan", "JAKSEL"),
        ("Jakarta Pusat", "JAKPUS"),
        ("Kota Tangerang Selatan", "TANGSEL"),
        ("Kab. Bekasi", "BEKASI"),
        ("Surabaya", None),
        (None, None),
    ],
)
def test_region_aliases_collapse_to_one_zone(text, expected):
    assert canonical_region(text) == expected


def test_longer_region_alias_wins_over_shorter_one():
    assert canonical_region("Tangerang Selatan") == "TANGSEL"


@pytest.mark.parametrize(
    ("form", "expected"),
    [("Unjuk rasa", "unjuk_rasa"), ("Pertunjukan Seni", "giat_masyarakat"), (None, None)],
)
def test_kind_from_form_field(form, expected):
    assert kind_from_form(form) == expected


def test_dedupe_merges_a_report_posted_twice():
    actions = actions_of(LABELED) + actions_of(LABELED)
    assert len(dedupe(actions)) == len(actions_of(LABELED))


def test_dedupe_keeps_the_more_complete_record():
    rich, sparse = actions_of(LABELED)[0], actions_of(LABELED)[0]
    sparse.leader = None
    sparse.demand = None
    kept = dedupe([sparse, rich])
    assert kept[0].leader == "Nama Contoh A"


def test_leader_is_withheld_by_default():
    payload = digest(extract(parse_messages(LABELED)), publisher="Relay Contoh")
    assert payload["redacted"] is True
    assert all("leader" not in a for a in payload["actions"])


def test_leader_is_present_only_when_explicitly_requested():
    payload = digest(
        extract(parse_messages(LABELED)), publisher="Relay Contoh", include_pii=True
    )
    assert payload["redacted"] is False
    assert any(a.get("leader") for a in payload["actions"])


def test_digest_counts_crowd_separately_per_kind():
    counts = digest(extract(parse_messages(LABELED)), publisher="Relay Contoh")["counts"]
    assert counts["by_kind"]["unjuk_rasa"]["crowd_reported"] == 115
    assert counts["by_kind"]["giat_masyarakat"]["crowd_reported"] == 2000


def test_digest_records_the_relay_as_a_low_reliability_source():
    payload = digest(extract(parse_messages(LABELED)), publisher="Relay Contoh")
    assert payload["source"]["reliability"] == "C3"


def test_phone_numbers_never_reach_the_dataset():
    text = """18/10/26 21.25 - Pelapor Contoh: *Rengiat wil Jakarta Pusat 19 Oktober 2026 :*

*1.* Pukul 12.00 WIB, Tempat Lokasi Contoh Sembilan, Pelaksana Organisasi Contoh H, Pimpinan Nama Contoh H (0812-0000-0000), Jumlah ± 20 orang, Tuntutan Tuntutan contoh keenam.
"""
    action = actions_of(text)[0]
    assert "0812" not in (action.leader or "")


def test_strip_phone_numbers_replaces_rather_than_deletes():
    assert "disunting" in strip_phone_numbers("hubungi +62 812 3456 7890 ya")


def test_sender_token_is_stable_and_hides_the_number():
    token = sender_token("+62 812-0000-0000")
    assert token == sender_token("+62 812-0000-0000")
    assert "0812" not in token and "812" not in token.split("-")[1][:3]


def test_fragment_claims_report_the_report_not_the_event():
    fragment = sitrep_fragment(
        extract(parse_messages(LABELED)), "2026-10-19", publisher="Relay Contoh"
    )
    assert all(c["text"].startswith("Relay melaporkan") for c in fragment["section"]["claims"])


def test_fragment_tags_every_claim_and_cites_the_relay():
    fragment = sitrep_fragment(
        extract(parse_messages(LABELED)), "2026-10-19", publisher="Relay Contoh"
    )
    for claim in fragment["section"]["claims"]:
        assert claim["tag"] == "FACT"
        assert claim["source_ids"] == [fragment["source"]["id"]]


def test_fragment_alerts_cover_demonstrations_only():
    fragment = sitrep_fragment(
        extract(parse_messages(LABELED)), "2026-10-19", publisher="Relay Contoh"
    )
    assert len(fragment["alerts"]) == 2


def test_fragment_horizon_follows_distance_from_the_edition_date():
    extraction = extract(parse_messages(LABELED))
    same_day = sitrep_fragment(extraction, "2026-10-19", publisher="Relay Contoh")
    day_before = sitrep_fragment(extraction, "2026-10-18", publisher="Relay Contoh")
    assert same_day["alerts"][0]["horizon"] == "0-24h"
    assert day_before["alerts"][0]["horizon"] == "0-72h"


def test_fragment_states_absence_rather_than_inventing_content():
    fragment = sitrep_fragment(
        extract(parse_messages(LABELED)), "2027-01-01", publisher="Relay Contoh"
    )
    assert fragment["alerts"] == []
    assert "Data belum tersedia" in fragment["section"]["claims"][0]["text"]


def test_fragment_carries_no_risk_scores():
    fragment = sitrep_fragment(
        extract(parse_messages(LABELED)), "2026-10-19", publisher="Relay Contoh"
    )
    assert "risk" not in fragment


def test_missing_crowd_figure_is_stated_not_guessed():
    text = """18/10/26 21.25 - Pelapor Contoh: *Rengiat wil Jakarta Pusat 19 Oktober 2026 :*

*1.* Pukul 12.00 WIB, Tempat Lokasi Contoh Sepuluh, Pelaksana Organisasi Contoh I, Pimpinan Nama Contoh I, Tuntutan Tuntutan contoh ketujuh.
"""
    extraction = extract(parse_messages(text))
    fragment = sitrep_fragment(extraction, "2026-10-19", publisher="Relay Contoh")
    assert extraction.actions[0].crowd_reported is None
    assert "Data belum tersedia" in fragment["section"]["claims"][0]["text"]
