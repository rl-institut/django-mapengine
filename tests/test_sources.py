"""Tests for testing sources module"""

from django.conf import settings

from django_mapengine import sources


def test_region_sources_from_settings():
    """Test region sources from settings"""

    region_sources = list(sources.get_region_sources())

    assert len(region_sources) == 2

    assert isinstance(region_sources[0], sources.MapSource)
    assert region_sources[0].name == "municipality"
    assert region_sources[0].type == "vector"
    assert region_sources[0].promote_id == "id"
    assert len(region_sources[0].tiles) == 1
    assert region_sources[0].tiles[0] == "map/municipality_mvt/{z}/{x}/{y}/"
    assert region_sources[0].url is None
    assert region_sources[0].minzoom is None
    assert region_sources[0].maxzoom is None

    assert isinstance(region_sources[1], sources.MapSource)
    assert region_sources[1].name == "district"
    assert region_sources[1].type == "vector"
    assert region_sources[1].promote_id == "id"
    assert len(region_sources[1].tiles) == 1
    assert region_sources[1].tiles[0] == "map/district_mvt/{z}/{x}/{y}/"
    assert region_sources[1].url is None
    assert region_sources[1].minzoom is None
    assert region_sources[1].maxzoom is None


def test_distilled_region_sources_from_settings():
    """Test region sources from settings using distilled option"""
    settings.MAP_ENGINE_USE_DISTILLED_MVTS = True

    region_sources = list(sources.get_region_sources())

    assert len(region_sources) == 2

    assert isinstance(region_sources[0], sources.MapSource)
    assert region_sources[0].name == "municipality"
    assert region_sources[0].type == "vector"
    assert region_sources[0].promote_id == "id"
    assert len(region_sources[0].tiles) == 1
    assert region_sources[0].tiles[0] == "static/mvts/{z}/{x}/{y}/municipality.mvt"
    assert region_sources[0].url is None
    assert region_sources[0].minzoom is None
    assert region_sources[0].maxzoom == 11

    assert isinstance(region_sources[1], sources.MapSource)
    assert region_sources[1].name == "district"
    assert region_sources[1].type == "vector"
    assert region_sources[1].promote_id == "id"
    assert len(region_sources[1].tiles) == 1
    assert region_sources[1].tiles[0] == "map/district_mvt/{z}/{x}/{y}/"
    assert region_sources[1].url is None
    assert region_sources[1].minzoom is None
    assert region_sources[1].maxzoom is None


def test_static_sources_from_settings():
    """Test static sources from setings"""
    settings.MAP_ENGINE_USE_DISTILLED_MVTS = False

    static_sources = list(sources.get_static_sources())

    assert len(static_sources) == 1

    assert isinstance(static_sources[0], sources.MapSource)
    assert static_sources[0].name == "static"
    assert static_sources[0].type == "vector"
    assert static_sources[0].promote_id == "id"
    assert len(static_sources[0].tiles) == 1
    assert static_sources[0].tiles[0] == "map/static_mvt/{z}/{x}/{y}/"
    assert static_sources[0].url is None
    assert static_sources[0].minzoom is None
    assert static_sources[0].maxzoom is None


def test_distilled_static_sources_from_settings():
    """Test static sources from setings while using distilled option"""
    settings.MAP_ENGINE_USE_DISTILLED_MVTS = True

    static_sources = list(sources.get_static_sources())

    assert len(static_sources) == 2

    assert isinstance(static_sources[0], sources.MapSource)
    assert static_sources[0].name == "static"
    assert static_sources[0].type == "vector"
    assert static_sources[0].promote_id == "id"
    assert len(static_sources[0].tiles) == 1
    assert static_sources[0].tiles[0] == "map/static_mvt/{z}/{x}/{y}/"
    assert static_sources[0].url is None
    assert static_sources[0].minzoom is None
    assert static_sources[0].maxzoom is None

    assert isinstance(static_sources[1], sources.MapSource)
    assert static_sources[1].name == "static_distilled"
    assert static_sources[1].type == "vector"
    assert static_sources[1].promote_id == "id"
    assert len(static_sources[1].tiles) == 1
    assert static_sources[1].tiles[0] == "static/mvts/{z}/{x}/{y}/static.mvt"
    assert static_sources[1].url is None
    assert static_sources[1].minzoom is None
    assert static_sources[1].maxzoom is None
