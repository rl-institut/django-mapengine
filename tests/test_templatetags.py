"""Tests for the mapengine_map template tag."""

import pytest
from django.template import Context, Template
from django.test import RequestFactory

from django_mapengine import setup


@pytest.fixture
def request_factory():
    return RequestFactory()


def test_mapengine_map_tag_renders_container_and_json_for_named_map(request_factory):
    template = Template('{% load mapengine_tags %}{% mapengine_map "default" %}')
    request = request_factory.get("/")

    rendered = template.render(Context({"request": request}))

    assert 'id="map-default"' in rendered
    assert 'id="mapengine_setup_default"' in rendered
    assert 'id="mapengine_store_cold_init_default"' in rendered


def test_mapengine_map_tag_defaults_to_default_map(request_factory):
    template = Template("{% load mapengine_tags %}{% mapengine_map %}")
    request = request_factory.get("/")

    rendered = template.render(Context({"request": request}))

    assert 'id="map-default"' in rendered


def test_mapengine_map_tag_includes_scripts_once_per_request(request_factory, settings):
    settings.MAP_ENGINE_MAPS = {
        "overview": setup.MapConfig(name="overview", center=[0, 0], zoom=1),
        "detail": setup.MapConfig(name="detail", center=[1, 1], zoom=2),
    }
    template = Template('{% load mapengine_tags %}{% mapengine_map "overview" %}{% mapengine_map "detail" %}')
    request = request_factory.get("/")

    rendered = template.render(Context({"request": request}))

    assert 'id="map-overview"' in rendered
    assert 'id="map-detail"' in rendered
    assert rendered.count("django_mapengine/js/init.js") == 1


def test_mapengine_map_tag_bundles_legend_and_basemap_scripts(request_factory):
    """
    legend.js/basemaps.js must be bundled: init.js unconditionally calls their setup functions.

    Parameters
    ----------
    request_factory : RequestFactory
        Fixture building a bare HttpRequest.
    """
    template = Template('{% load mapengine_tags %}{% mapengine_map "default" %}')
    request = request_factory.get("/")

    rendered = template.render(Context({"request": request}))

    assert "django_mapengine/js/legend.js" in rendered
    assert "django_mapengine/js/basemaps.js" in rendered


def test_mapengine_map_tag_unknown_name_raises(request_factory):
    template = Template('{% load mapengine_tags %}{% mapengine_map "unknown" %}')
    request = request_factory.get("/")

    with pytest.raises(KeyError):
        template.render(Context({"request": request}))
