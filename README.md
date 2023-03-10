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

1. Add "oemof" to your INSTALLED_APPS setting like this::
    ```
        INSTALLED_APPS = [
            ...
            'django_mapengine',
        ]
    ```

2. Configure map engine by setting zoom levels, regions and styles folder in sites settings.py.
   Example settings:
   ```
       MAP_ENGINE_STYLES_FOLDER = "app_name/static/config/"
       MAP_ENGINE_ZOOM_LEVELS = {
           "municipality": core.Zoom(8, 12),
       }
       MAP_ENGINE_REGIONS = ("municipality",)
   ```
