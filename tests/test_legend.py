"""Tests for map-scoped legends."""

from django_mapengine import legend, setup


def test_legend_item_checked_defaults_from_default_map_startup_layers(settings):
    settings.MAP_ENGINE_LAYERS_AT_STARTUP = ["wind"]

    checked_item = legend.LegendItem("wind")
    unchecked_item = legend.LegendItem("pvroof")

    assert checked_item.checked is True
    assert unchecked_item.checked is False


def test_legend_item_checked_defaults_from_named_map(settings):
    settings.MAP_ENGINE_MAPS = {
        "overview": setup.MapConfig(name="overview", center=[0, 0], zoom=1, layers_at_startup=["wind"]),
    }

    item = legend.LegendItem("wind", map_name="overview")

    assert item.checked is True


def test_legend_carries_map_name_onto_its_items(settings):
    settings.MAP_ENGINE_MAPS = {
        "detail": setup.MapConfig(name="detail", center=[0, 0], zoom=1, layers_at_startup=["wind"]),
    }

    legend_instance = legend.Legend.from_layer_names("turbines", ["wind"], map_name="detail")

    assert legend_instance.map_name == "detail"
    item = legend_instance.categories["turbines"][0]
    assert item.map_name == "detail"
    assert item.checked is True


def test_legend_from_items_carries_map_name_onto_its_items(settings):
    """
    from_items must propagate map_name the same way from_layer_names does.

    Parameters
    ----------
    settings : SettingsWrapper
        pytest-django fixture to override settings for this test only.
    """
    settings.MAP_ENGINE_MAPS = {
        "detail": setup.MapConfig(name="detail", center=[0, 0], zoom=1, layers_at_startup=["wind"]),
    }

    legend_instance = legend.Legend.from_items("turbines", ["wind"], map_name="detail")

    item = legend_instance.categories["turbines"][0]
    assert item.map_name == "detail"
    assert item.checked is True
