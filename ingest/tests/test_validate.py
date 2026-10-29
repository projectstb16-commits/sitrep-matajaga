import copy

import pytest

from mjs_ingest.validate import errors, passed, validate


def base_doc():
    return {
        "edition": {
            "id": "MJS-2026-10-29-032",
            "date": "2026-10-29",
            "sequence": 32,
            "classification": "PREVIEW_OPEN_REDISTRIBUTION",
            "tier": "B",
            "methodology": "MSRM v1.1",
        },
        "risk": {
            "composite": 52,
            "pillars": {
                "security": 60,
                "transport": 55,
                "economy": 50,
                "cyber": 45,
                "weather": 40,
            },
        },
        "zones": [{"zone": "JAKTIM", "score": 61}],
        "alerts": [
            {
                "horizon": "0-6h",
                "headline": "Genangan pada ruas tol dalam kota",
                "claim_tag": "FACT",
                "source_ids": ["s1"],
            }
        ],
        "sections": [
            {
                "key": "executive_summary",
                "title": "Executive Summary",
                "claims": [
                    {"text": "Genangan tercatat di Jakarta Timur.", "tag": "FACT", "source_ids": ["s1"]},
                    {"text": "Tekanan pada rute logistik timur meningkat.", "tag": "ANALYSIS"},
                ],
            }
        ],
        "outlook": [
            {"horizon": "H+1", "claim": {"text": "Curah hujan bertahan.", "tag": "ASSUMPTION"}}
        ],
        "sources": [{"id": "s1", "reliability": "B2", "publisher": "BMKG"}],
    }


def codes(doc):
    return {f.code for f in validate(doc)}


def test_clean_document_passes():
    findings = validate(base_doc())
    assert passed(findings), [str(f) for f in findings]


def test_edition_id_format_is_enforced():
    doc = base_doc()
    doc["edition"]["id"] = "MJS-2026-10-29-32"
    assert "EDITION_ID_FORMAT" in codes(doc)


def test_edition_date_must_match_id():
    doc = base_doc()
    doc["edition"]["date"] = "2026-10-28"
    assert "EDITION_DATE_MISMATCH" in codes(doc)


def test_edition_sequence_must_match_id():
    doc = base_doc()
    doc["edition"]["sequence"] = 31
    assert "EDITION_SEQUENCE_MISMATCH" in codes(doc)


def test_methodology_label_is_fixed():
    doc = base_doc()
    doc["edition"]["methodology"] = "MSRM v2"
    assert "METHODOLOGY_LABEL" in codes(doc)


def test_preview_classification_requires_tier_b():
    doc = base_doc()
    doc["edition"]["tier"] = "A"
    found = codes(doc)
    assert "CLASSIFICATION_TIER_MISMATCH" in found
    assert "TIER_A_NOT_ACTIVATED" in found


def test_composite_must_match_the_pillars_it_claims_to_summarise():
    doc = base_doc()
    doc["risk"]["composite"] = 75
    assert "COMPOSITE_MISMATCH" in codes(doc)


def test_floored_composite_is_reported_as_a_warning_not_an_error():
    doc = base_doc()
    doc["risk"]["pillars"] = {
        "security": 30,
        "transport": 20,
        "economy": 20,
        "cyber": 10,
        "weather": 85,
    }
    doc["risk"]["composite"] = 60
    findings = validate(doc)
    assert passed(findings), [str(f) for f in findings]
    assert "COMPOSITE_FLOORED" in {f.code for f in findings}


def test_fact_claim_without_a_source_is_an_error():
    doc = base_doc()
    doc["sections"][0]["claims"][0].pop("source_ids")
    assert "FACT_WITHOUT_SOURCE" in codes(doc)


def test_fact_claim_may_state_that_data_is_unavailable_without_a_source():
    doc = base_doc()
    doc["sections"][0]["claims"][0] = {
        "text": "Data belum tersedia untuk ruas tol Cikampek.",
        "tag": "FACT",
    }
    assert passed(validate(doc))


def test_untagged_claim_is_an_error():
    doc = base_doc()
    doc["sections"][0]["claims"][1].pop("tag")
    assert "CLAIM_TAG_MISSING" in codes(doc)


def test_dangling_source_reference_is_an_error():
    doc = base_doc()
    doc["sections"][0]["claims"][0]["source_ids"] = ["s9"]
    assert "SOURCE_REF_DANGLING" in codes(doc)


def test_duplicate_source_id_is_an_error():
    doc = base_doc()
    doc["sources"].append({"id": "s1", "reliability": "A1", "publisher": "Polda Metro Jaya"})
    assert "SOURCE_ID_DUPLICATE" in codes(doc)


def test_source_reliability_must_use_a_known_tier():
    doc = base_doc()
    doc["sources"][0]["reliability"] = "D4"
    assert "SOURCE_RELIABILITY_TIER" in codes(doc)


@pytest.mark.parametrize(
    "mention",
    ["Control Risks", "Crisis24", "Deloitte", "PwC", "Ernst & Young"],
)
def test_forbidden_firm_mentions_are_rejected(mention):
    doc = base_doc()
    doc["sections"][0]["claims"][1]["text"] = f"Dibandingkan laporan {mention} pekan lalu."
    assert "FORBIDDEN_MENTION" in codes(doc)


def test_uppercase_ey_is_caught_but_ordinary_words_are_not():
    doc = base_doc()
    doc["sections"][0]["claims"][1]["text"] = "Laporan EY menyebut tekanan serupa."
    assert "FORBIDDEN_MENTION" in codes(doc)

    clean = base_doc()
    clean["sections"][0]["claims"][1]["text"] = "They key issue is the eyewitness account."
    assert "FORBIDDEN_MENTION" not in codes(clean)


def test_emoji_is_rejected():
    doc = base_doc()
    doc["sections"][0]["title"] = "Executive Summary ✅"
    assert "EMOJI_PRESENT" in codes(doc)


def test_alert_horizon_must_be_known():
    doc = base_doc()
    doc["alerts"][0]["horizon"] = "0-12h"
    assert "HORIZON_UNKNOWN" in codes(doc)


def test_validation_reports_every_problem_in_one_pass():
    doc = base_doc()
    doc["edition"]["methodology"] = "MSRM v2"
    doc["risk"]["composite"] = 99
    doc["sections"][0]["claims"][0].pop("source_ids")
    assert len(errors(validate(doc))) >= 3


def test_validation_does_not_mutate_the_document():
    doc = base_doc()
    before = copy.deepcopy(doc)
    validate(doc)
    assert doc == before
