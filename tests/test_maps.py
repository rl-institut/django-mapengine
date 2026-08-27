"""Tests for the multi-map registry (django_mapengine.maps)."""

import pytest
from django.conf import settings
from django.test import RequestFactory

from django_mapengine import maps, setup


@pytest.fixture
def request_factory():
    return RequestFactory()


def test_get_map_config_without_map_engine_maps_returns_default():
    """Without MAP_ENGINE_MAPS set, 'default' is synthesized from flat settings."""
    map_config = maps.get_map_config("default")

    assert isinstance(map_config, setup.MapConfig)
    assert map_config.name == "default"
    assert map_config.center == settings.MAP_ENGINE_CENTER_AT_STARTUP
    assert map_config.zoom == settings.MAP_ENGINE_ZOOM_AT_STARTUP
    assert map_config.layers is None
    assert map_config.layers_at_startup == settings.MAP_ENGINE_LAYERS_AT_STARTUP
    assert map_config.hover_layers == settings.MAP_ENGINE_HOVER_LAYERS
    assert map_config.choropleths == settings.MAP_ENGINE_CHOROPLETHS
    assert map_config.popups == settings.MAP_ENGINE_POPUPS


def test_get_map_config_defaults_to_default_name():
    """Calling without a name resolves to the 'default' map."""
    assert maps.get_map_config() == maps.get_map_config("default")


def test_get_map_config_unknown_name_without_map_engine_maps_raises():
    """Only 'default' exists when MAP_ENGINE_MAPS is unset."""
    with pytest.raises(KeyError):
        maps.get_map_config("overview")


def test_get_map_config_looks_up_map_engine_maps(settings):
    """
    When MAP_ENGINE_MAPS is set, named configs are looked up from it.

    Parameters
    ----------
    settings : SettingsWrapper
        pytest-django fixture to override settings for this test only.
    """
    overview = setup.MapConfig(name="overview", center=[10, 20], zoom=5, layers=["wind"])
    settings.MAP_ENGINE_MAPS = {"overview": overview}

    assert maps.get_map_config("overview") is overview


def test_get_map_config_unknown_name_with_map_engine_maps_raises(settings):
    """
    An unknown map name raises KeyError, listing known maps.

    Parameters
    ----------
    settings : SettingsWrapper
        pytest-django fixture to override settings for this test only.
    """
    settings.MAP_ENGINE_MAPS = {"overview": setup.MapConfig(name="overview", center=[0, 0], zoom=1)}

    with pytest.raises(KeyError, match="overview"):
        maps.get_map_config("detail")


def test_map_config_get_setup_uses_map_name_as_container():
    """The maplibre setup dict scopes its container id to the map name."""
    map_config = setup.MapConfig(name="detail", center=[1, 2], zoom=8, min_zoom=3, max_zoom=15)

    map_setup = map_config.get_setup()

    assert map_setup["container"] == "map-detail"
    assert map_setup["center"] == [1, 2]
    assert map_setup["zoom"] == 8
    assert map_setup["minZoom"] == 3
    assert map_setup["maxZoom"] == 15
    assert "maxBounds" not in map_setup


def test_map_config_get_setup_falls_back_to_global_zoom_bounds():
    """Unset min/max zoom and bounds fall back to the global MAP_ENGINE_* settings."""
    map_config = setup.MapConfig(name="detail", center=[1, 2], zoom=8)

    map_setup = map_config.get_setup()

    assert map_setup["minZoom"] == settings.MAP_ENGINE_MIN_ZOOM
    assert map_setup["maxZoom"] == settings.MAP_ENGINE_MAX_ZOOM


def test_map_config_get_setup_includes_max_bounds_when_set():
    """maxBounds is only included when given."""
    map_config = setup.MapConfig(name="detail", center=[1, 2], zoom=8, max_bounds=[[0, 0], [1, 1]])

    assert map_config.get_setup()["maxBounds"] == [[0, 0], [1, 1]]


def test_build_map_context_scopes_setup_and_store_to_map(request_factory):
    """
    build_map_context returns a context dict for exactly one named map.

    Parameters
    ----------
    request_factory : RequestFactory
        Fixture building a bare HttpRequest.
    """
    map_config = setup.MapConfig(
        name="overview", center=[1, 2], zoom=8, layers=["wind"], layers_at_startup=["wind"], hover_layers=["wind"]
    )
    request = request_factory.get("/")

    context = maps.build_map_context(map_config, request)

    assert context["map_name"] == "overview"
    assert context["mapengine_setup"]["container"] == "map-overview"
    assert context["mapengine_store_cold_init"]["hover_layers"] == ["wind", "wind_distilled"]
    assert context["mapengine_layers_at_startup"] == ["wind", "wind_distilled"]


def test_build_map_context_filters_layers_to_map_subset(request_factory):
    """
    Only layers listed in map_config.layers (plus their derived layers) are included.

    Parameters
    ----------
    request_factory : RequestFactory
        Fixture building a bare HttpRequest.
    """
    map_config = setup.MapConfig(name="overview", center=[1, 2], zoom=8, layers=["wind"])
    request = request_factory.get("/")

    context = maps.build_map_context(map_config, request)

    layer_ids = {layer["id"] for layer in context["mapengine_layers"]}
    assert layer_ids == {"wind", "wind_cluster", "wind_cluster_count"}


def test_build_map_context_includes_all_layers_when_subset_not_given(request_factory):
    """
    map_config.layers=None (back-compat default) means no filtering.

    Parameters
    ----------
    request_factory : RequestFactory
        Fixture building a bare HttpRequest.
    """
    map_config = maps.get_map_config("default")
    request = request_factory.get("/")

    context = maps.build_map_context(map_config, request)

    layer_ids = {layer["id"] for layer in context["mapengine_layers"]}
    assert "pvroof" in layer_ids
    assert "municipality" in layer_ids
