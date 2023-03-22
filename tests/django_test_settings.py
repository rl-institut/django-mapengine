"""Django settings used in tests"""

from django_mapengine import setup

INSTALLED_APPS = ["django_mapengine", "tests.test_app.apps.TestConf"]

MAP_ENGINE_CENTER_AT_STARTUP = [1, 2]
MAP_ENGINE_ZOOM_AT_STARTUP = 8

MAP_ENGINE_STYLES_FOLDER = "tests/test_data/styles"

MAP_ENGINE_ZOOM_LEVELS = {
    "municipality": setup.Zoom(5, 10),
    "district": setup.Zoom(10, 12),
}
MAP_ENGINE_USE_DISTILLED_MVTS = False
MAP_ENGINE_MAX_DISTILLED_ZOOM = 10
MAP_ENGINE_CLUSTER_ZOOM = 8

MAP_ENGINE_API_MVTS = {
    "municipality": [
        setup.MVTAPI("municipality", "test_app", "Municipality"),
        setup.MVTAPI("municipalitylabel", "test_app", "Municipality", "label_tiles"),
    ],
    "static": [setup.MVTAPI("wind", "test_app", "WindTurbine"), setup.MVTAPI("pvroof", "test_app", "PVRoof")],
}

MAP_ENGINE_API_CLUSTERS = [
    setup.ClusterAPI("wind", "test_app", "WindTurbine"),
    setup.ClusterAPI("pvroof", "test_app", "PVroof"),
]
