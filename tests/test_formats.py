import pytest

from hunt.formats import format_mmr, MMR_RANGES, STAR_SYMBOL


@pytest.mark.parametrize("mmr, expected_stars", ((mmr, i) for i, mmr in enumerate(MMR_RANGES, start=1)))
def test_format_mmr(mmr: int, expected_stars: int) -> None:
    assert format_mmr(mmr).count(STAR_SYMBOL) == expected_stars
