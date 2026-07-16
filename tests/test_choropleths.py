"""Test for choropleths."""

import pathlib

import pytest

from django_mapengine import choropleth

TEST_FOLDER = pathlib.Path(__file__).parent
TEST_CHOROPLETH_STYLES_FILE = TEST_FOLDER / "test_data" / "styles" / "choropleths.json"

CHOROPLETHS = choropleth.Choropleth(TEST_CHOROPLETH_STYLES_FILE)


@pytest.mark.parametrize(
    ("min_value", "max_value", "expected"),
    [
        (5, 65, (0, 100)),
        (85, 105, (80, 120)),
        (50, 405, (0, 500)),
        (3, 10, (0, 10)),
        (5, 11, (0, 20)),
        (0.1, 5, (0, 5)),
        (0.01, 0.1, (0, 0.1)),
        (42, 42, (0, 50)),
        (0, 0, (0, 1)),
    ],
)
def test_calculate_nice_bounds(min_value: float, max_value: float, expected: tuple[float, float]) -> None:
    """Test nice-number bound calculation for dynamic choropleth values."""
    assert CHOROPLETHS._Choropleth__calculate_nice_bounds(min_value, max_value) == expected  # noqa: SLF001


def test_choropleths_with_values() -> None:
    """Test choropleth with static values."""
    fill_color = CHOROPLETHS.get_fill_color("with_values")
    assert fill_color == [
        "interpolate",
        ["linear"],
        ["feature-state", "with_values"],
        0.3,
        "rgb(224, 243, 219)",
        0.6,
        "rgb(168, 221, 181)",
        0.8,
        "rgb(67, 162, 202)",
    ]


def test_choropleths_without_values() -> None:
    """Test dynamic choropleth with values from results."""
    fill_color = CHOROPLETHS.get_fill_color("without_values", [10, 40, 50, 310])
    assert fill_color == [
        "interpolate",
        ["linear"],
        ["feature-state", "without_values"],
        0.0,
        "rgb(255, 255, 204)",
        166.66666666666666,
        "rgb(199, 233, 180)",
        333.3333333333333,
        "rgb(127, 205, 187)",
        500.0,
        "rgb(65, 182, 196)",
        666.6666666666666,
        "rgb(44, 127, 184)",
        833.3333333333333,
        "rgb(37, 52, 148)",
    ]
