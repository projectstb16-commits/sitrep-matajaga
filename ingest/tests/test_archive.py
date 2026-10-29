import json

import pytest

from mjs_ingest.archive import next_sequence, scan, to_index


def write(directory, name):
    (directory / name).write_text("x", encoding="utf-8")


def test_scan_pairs_the_two_products_of_one_edition(tmp_path):
    write(tmp_path, "MJS-2026-10-29-032-PREVIEW-EN.docx")
    write(tmp_path, "MJS-2026-10-29-032-WA-ID.txt")

    records = scan(tmp_path)

    assert len(records) == 1
    record = records[0]
    assert record.edition_id == "MJS-2026-10-29-032"
    assert record.sequence == 32
    assert record.complete
    assert record.issues == []


def test_scan_orders_newest_edition_first(tmp_path):
    for seq, date in (("030", "2026-10-27"), ("031", "2026-10-28"), ("032", "2026-10-29")):
        write(tmp_path, f"MJS-{date}-{seq}-PREVIEW-EN.docx")
        write(tmp_path, f"MJS-{date}-{seq}-WA-ID.txt")

    assert [r.sequence for r in scan(tmp_path)] == [32, 31, 30]


def test_incomplete_edition_is_flagged_not_dropped(tmp_path):
    write(tmp_path, "MJS-2026-10-29-032-PREVIEW-EN.docx")

    record = scan(tmp_path)[0]

    assert not record.complete
    assert any("versi WA" in issue for issue in record.issues)


def test_sequence_collision_across_dates_is_flagged(tmp_path):
    write(tmp_path, "MJS-2026-10-28-032-PREVIEW-EN.docx")
    write(tmp_path, "MJS-2026-10-28-032-WA-ID.txt")
    write(tmp_path, "MJS-2026-10-29-032-PREVIEW-EN.docx")
    write(tmp_path, "MJS-2026-10-29-032-WA-ID.txt")

    records = scan(tmp_path)

    assert len(records) == 2
    assert all(any("konflik penomoran" in i for i in r.issues) for r in records)


def test_unparsed_filenames_are_surfaced(tmp_path):
    write(tmp_path, "catatan rapat.docx")

    records = scan(tmp_path)

    assert records[-1].edition_id == "UNPARSED"
    assert any("di luar pola penomoran" in i for i in records[-1].issues)


def test_next_sequence_is_highest_plus_one(tmp_path):
    write(tmp_path, "MJS-2026-10-29-032-PREVIEW-EN.docx")
    write(tmp_path, "MJS-2026-10-29-032-WA-ID.txt")

    assert next_sequence(scan(tmp_path)) == 33


def test_next_sequence_starts_at_one_for_an_empty_archive(tmp_path):
    assert next_sequence(scan(tmp_path)) == 1


def test_next_sequence_ignores_unparsed_entries(tmp_path):
    write(tmp_path, "draft.txt")
    assert next_sequence(scan(tmp_path)) == 1


def test_index_is_serialisable_json_carrying_the_next_counter(tmp_path):
    write(tmp_path, "MJS-2026-10-29-032-PREVIEW-EN.docx")
    write(tmp_path, "MJS-2026-10-29-032-WA-ID.txt")

    payload = json.loads(to_index(scan(tmp_path)))

    assert payload["next_sequence"] == 33
    assert payload["editions"][0]["edition_id"] == "MJS-2026-10-29-032"


def test_scan_rejects_a_path_that_is_not_a_directory(tmp_path):
    target = tmp_path / "file.txt"
    target.write_text("x", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        scan(target)


def test_hidden_files_are_ignored(tmp_path):
    write(tmp_path, ".gitkeep")
    write(tmp_path, ".DS_Store")

    assert scan(tmp_path) == []
