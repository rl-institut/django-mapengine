"""Tests for testing sources module"""

from django.conf import settings

import django_mapengine.setup
from django_mapengine import sources


def test_static_sources_from_settings():
    """Test static sources from setings"""
    settings.MAP_ENGINE_USE_DISTILLED_MVTS = False

    static_sources = list(sources.get_static_sources())

    assert len(static_sources) == 1

    assert isinstance(static_sources[0], django_mapengine.setup.MapSource)
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

    assert isinstance(static_sources[0], django_mapengine.setup.MapSource)
    assert static_sources[0].name == "static"
    assert static_sources[0].type == "vector"
    assert static_sources[0].promote_id == "id"
    assert len(static_sources[0].tiles) == 1
    assert static_sources[0].tiles[0] == "map/static_mvt/{z}/{x}/{y}/"
    assert static_sources[0].url is None
    assert static_sources[0].minzoom is None
    assert static_sources[0].maxzoom is None

    assert isinstance(static_sources[1], django_mapengine.setup.MapSource)
    assert static_sources[1].name == "static_distilled"
    assert static_sources[1].type == "vector"
    assert static_sources[1].promote_id == "id"
    assert len(static_sources[1].tiles) == 1
    assert static_sources[1].tiles[0] == "static/mvts/{z}/{x}/{y}/static.mvt"
    assert static_sources[1].url is None
    assert static_sources[1].minzoom is None
    assert static_sources[1].maxzoom is None


def test_cluster_sources_from_settings():
    """Test cluster sources from setings"""
    settings.MAP_ENGINE_USE_DISTILLED_MVTS = False

    cluster_sources = list(sources.get_cluster_sources())

    assert len(cluster_sources) == 2

    assert isinstance(cluster_sources[0], django_mapengine.setup.MapSource)
    assert cluster_sources[0].name == "wind"
    assert cluster_sources[0].type == "geojson"
    assert cluster_sources[0].promote_id == "id"
    assert cluster_sources[0].tiles is None
    assert cluster_sources[0].url == "map/clusters/wind.geojson"
    assert cluster_sources[0].minzoom is None
    assert cluster_sources[0].maxzoom is None

    assert isinstance(cluster_sources[1], django_mapengine.setup.MapSource)
    assert cluster_sources[1].name == "pvroof"
    assert cluster_sources[1].type == "geojson"
    assert cluster_sources[1].promote_id == "id"
    assert cluster_sources[1].tiles is None
    assert cluster_sources[1].url == "map/clusters/pvroof.geojson"
    assert cluster_sources[1].minzoom is None
    assert cluster_sources[1].maxzoom is None
