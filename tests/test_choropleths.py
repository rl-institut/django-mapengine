"""Test for choropleths."""

import pathlib

from django_mapengine import choropleth

TEST_FOLDER = pathlib.Path(__file__).parent
TEST_CHOROPLETH_STYLES_FILE = TEST_FOLDER / "test_data" / "styles" / "choropleths.json"

CHOROPLETHS = choropleth.Choropleth(TEST_CHOROPLETH_STYLES_FILE)


def test_choropleths_with_values() -> None:
    """Test choropleth with static values."""
    fill_color = CHOROPLETHS.get_fill_color("with_values")
    assert fill_color == [
        "interpolate",
        ["linear"],
        ["feature-state", "with_values"],
        0.3,
        "rgb(240, 249, 232)",
        0.6,
        "rgb(186, 228, 188)",
        0.8,
        "rgb(123, 204, 196)",
        1.0,
        "rgb(43, 140, 190)",
    ]


def test_choropleths_without_values() -> None:
    """Test dynamic choropleth with values from results."""
    fill_color = CHOROPLETHS.get_fill_color("without_values", [10, 40, 50, 310])
    assert fill_color == [
        "interpolate",
        ["linear"],
        ["feature-state", "without_values"],
        10.0,
        "rgb(255, 255, 204)",
        70.0,
        "rgb(199, 233, 180)",
        130.0,
        "rgb(127, 205, 187)",
        190.0,
        "rgb(65, 182, 196)",
        250.0,
        "rgb(44, 127, 184)",
        310.0,
        "rgb(37, 52, 148)",
    ]
