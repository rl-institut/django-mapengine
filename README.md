# Django-Mapengine

`django-mapengine` is a Django app to provide library for maplibre in backend. 
This includes
- html templates and JS files for maplibre 
- creation of maplibre sources and layers including choropleths, 
- provision of multi-vector-tiles from django models,
- distilling of map source views
- basic popups

## Requirements

Maplibre must be installed (i.e. via npm) and provided as JS framework

## Quick start

1. Add "django_mapengine" to your INSTALLED_APPS setting like this::
```python
    INSTALLED_APPS = [
        "...",
        'django_mapengine',
    ]
```

2. Include URLs from django_mapengine to your project:
```python
    urlpatterns = [
        "...",
        path("map/", include("django_mapengine.urls")),
    ]
```

3. Configure map engine by setting zoom levels, regions and styles folder in project settings.py.
   You can see all possible settings by looking into `django_mapengine.settings.py`.
   Example settings:

```python
    from django_mapengine import setup

MAP_ENGINE_CENTER_AT_STARTUP = [12.537917858911896, 51.80812518969171]
MAP_ENGINE_ZOOM_AT_STARTUP = 9
MAP_ENGINE_MAX_BOUNDS = [[11.280733017118229, 51.22918643452503], [13.616574868700604, 52.35515806663738]]

MAP_ENGINE_IMAGES = [core.MapImage("wind", "images/icons/i_wind.png")]

MAP_ENGINE_API_MVTS = {
    "municipality":
        [
            setup.MVTAPI("municipality", "map", "Municipality"),
            setup.MVTAPI("municipalitylabel", "map", "Municipality", "label_tiles"),
        ],
    "results": [setup.MVTAPI("results", "map", "Municipality")]
}

MAP_ENGINE_API_CLUSTERS = [
    setup.ClusterAPI("wind", "map", "WindTurbine"),
    setup.ClusterAPI("pvroof", "map", "PVroof"),
    setup.ClusterAPI("pvground", "map", "PVground"),
    setup.ClusterAPI("hydro", "map", "Hydro"),
    setup.ClusterAPI("biomass", "map", "Biomass"),
    setup.ClusterAPI("combustion", "map", "Combustion"),
]

MAP_ENGINE_STYLES_FOLDER = "digiplan/static/config/"
MAP_ENGINE_ZOOM_LEVELS = {
   "municipality": core.Zoom(8, 12),
}

MAP_ENGINE_POPUPS = ["results"]
```