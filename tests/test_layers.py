"""Tests for testing layers module"""

from django.conf import settings

from django_mapengine import layers, setup


def test_cluster_layers_from_settings():
    """Test cluster layers from settings"""
    settings.MAP_ENGINE_API_CLUSTERS = [
        setup.ClusterAPI("wind", "test_app", "WindTurbine"),
        setup.ClusterAPI("pvroof", "test_app", "PVroof"),
    ]
    cluster_layers = list(layers.get_cluster_layers())

    assert len(cluster_layers) == 2

    # pylint:disable=C0415
    from test_app import models  # Import here, otherwise app not ready

    assert isinstance(cluster_layers[0], layers.ClusterModelLayer)
    assert cluster_layers[0].id == "wind"
    assert issubclass(cluster_layers[0].model, models.WindTurbine)
    assert cluster_layers[0].source == "wind"

    assert isinstance(cluster_layers[1], layers.ClusterModelLayer)
    assert cluster_layers[1].id == "pvroof"
    assert issubclass(cluster_layers[1].model, models.PVRoof)
    assert cluster_layers[1].source == "pvroof"


def test_static_layers_from_settings():
    """Test static layers from settings"""
    settings.MAP_ENGINE_REGIONS = ("municipality",)
    settings.MAP_ENGINE_API_MVTS = {
        "municipality": [
            setup.MVTAPI("municipality", "test_app", "Municipality"),
            setup.MVTAPI("municipalitylabel", "test_app", "Municipality", "label_tiles"),
        ],
        "static": [setup.MVTAPI("wind", "test_app", "WindTurbine"), setup.MVTAPI("pvroof", "test_app", "PVRoof")],
    }
    static_layers = list(layers.get_static_layers())

    assert len(static_layers) == 2

    # pylint:disable=C0415
    from test_app import models  # Import here, otherwise app not ready

    assert isinstance(static_layers[0], layers.StaticModelLayer)
    assert static_layers[0].id == "wind"
    assert issubclass(static_layers[0].model, models.WindTurbine)
    assert static_layers[0].source == "static"

    assert isinstance(static_layers[1], layers.StaticModelLayer)
    assert static_layers[1].id == "pvroof"
    assert issubclass(static_layers[1].model, models.PVRoof)
    assert static_layers[1].source == "static"
