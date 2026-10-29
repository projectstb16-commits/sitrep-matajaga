import pytest

from mjs_ingest.msrm import (
    Band,
    DEFAULT_WEIGHTS,
    ScoreOutOfRange,
    band_of,
    composite,
    fill_of,
)


@pytest.mark.parametrize(
    ("score", "band"),
    [
        (0, Band.LOW),
        (39, Band.LOW),
        (40, Band.MODERATE),
        (59, Band.MODERATE),
        (60, Band.HIGH),
        (79, Band.HIGH),
        (80, Band.CRITICAL),
        (100, Band.CRITICAL),
    ],
)
def test_band_boundaries_are_inclusive(score, band):
    assert band_of(score) is band


@pytest.mark.parametrize("score", [-1, 101])
def test_band_rejects_out_of_range(score):
    with pytest.raises(ScoreOutOfRange):
        band_of(score)


def test_band_rejects_bool_masquerading_as_int():
    with pytest.raises(ScoreOutOfRange):
        band_of(True)


def test_fill_follows_band():
    assert fill_of(35) == fill_of(0)
    assert fill_of(85) != fill_of(35)


def test_composite_is_weighted_mean_when_no_pillar_is_critical():
    pillars = {"security": 60, "transport": 60, "economy": 60, "cyber": 60, "weather": 60}
    result = composite(pillars)
    assert result.score == 60
    assert result.band is Band.HIGH
    assert not result.was_floored


def test_composite_floors_to_high_when_one_pillar_is_critical():
    # Rata-rata berbobot sendiri menghasilkan band LOW walau cuaca CRITICAL.
    pillars = {"security": 30, "transport": 20, "economy": 20, "cyber": 10, "weather": 85}
    result = composite(pillars)
    assert result.weighted_raw < 40
    assert result.score == 60
    assert result.band is Band.HIGH
    assert result.floored_by == "weather"


def test_composite_does_not_lower_a_score_already_above_the_floor():
    pillars = {"security": 90, "transport": 85, "economy": 80, "cyber": 80, "weather": 85}
    result = composite(pillars)
    assert result.score > 60
    assert result.band is Band.CRITICAL


def test_composite_names_every_critical_pillar_when_floored():
    pillars = {"security": 85, "transport": 10, "economy": 10, "cyber": 90, "weather": 10}
    result = composite(pillars)
    assert result.floored_by == "security, cyber"


def test_composite_rejects_incomplete_pillars():
    with pytest.raises(ValueError, match="pilar belum lengkap"):
        composite({"security": 50})


def test_composite_rejects_unknown_pillar():
    pillars = {
        "security": 50,
        "transport": 50,
        "economy": 50,
        "cyber": 50,
        "weather": 50,
        "politics": 50,
    }
    with pytest.raises(ValueError, match="tidak dikenal"):
        composite(pillars)


def test_default_weights_cover_every_pillar_and_sum_to_one():
    assert set(DEFAULT_WEIGHTS) == {"security", "transport", "economy", "cyber", "weather"}
    assert round(sum(DEFAULT_WEIGHTS.values()), 6) == 1.0


def test_custom_weights_are_normalised_so_they_need_not_sum_to_one():
    pillars = {"security": 80, "transport": 40, "economy": 40, "cyber": 40, "weather": 40}
    equal_fractions = composite(pillars, weights=dict.fromkeys(DEFAULT_WEIGHTS, 0.2))
    equal_integers = composite(pillars, weights=dict.fromkeys(DEFAULT_WEIGHTS, 1.0))
    assert equal_fractions.score == equal_integers.score
