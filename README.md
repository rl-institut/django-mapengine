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

1. Add "django_mapengine" to your INSTALLED_APPS setting like this:
   ```python
   INSTALLED_APPS = [
        "...",
        'django_mapengine',
   ]
   ```
2. Install maplibre-gl and pubsub-js dependency by:
   ```shell
   npm install maplibre-gl pubsub-js
   ```
   and copy JS and CSS to your static folder.

3. Include URLs from django_mapengine to your project:
   ```python
   urlpatterns = [
       "...",
       path("map/", include("django_mapengine.urls")),
   ]
   ```

4. Configure map engine by setting zoom levels, regions and styles folder in project settings.py.
   You can see all possible settings by looking into `django_mapengine.settings.py`.
   Example settings:

   ```python
   from django_mapengine import setup

   MAP_ENGINE_CENTER_AT_STARTUP = [12.537917858911896, 51.80812518969171]
   MAP_ENGINE_ZOOM_AT_STARTUP = 9
   MAP_ENGINE_MAX_BOUNDS = [[11.280733017118229, 51.22918643452503], [13.616574868700604, 52.35515806663738]]

   MAP_ENGINE_IMAGES = [setup.MapImage("wind", "images/icons/i_wind.png")]

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

5. Add middleware to your middleware setup before Whitenoise middleware (or other static server middleware):
   ```python
   MIDDLEWARE = [
       "django.middleware.security.SecurityMiddleware",
       "django_mapengine.django_mapengine.middleware.MapEngineMiddleware",
       "whitenoise.middleware.WhiteNoiseMiddleware",
       ...
   ]
   ```

6. Add maplibre-gl, pubsub-js and mapengine JS, CSS and JSONs in template by:
   ```html
   {% block javascript %}
     {{ block.super }}
     {% compress js %}
       <script src="{% static 'vendors/maplibre/js/maplibre-gl.js' %}"></script>
       <script src="{% static 'vendors/pubsub/js/pubsub.js' %}"></script>
     {% endcompress %}
   {% endblock javascript %}

   {%  block inline_javascript %}
     {% include 'django_mapengine/map_json.html' %}
     {% compress js %}
       {% include 'django_mapengine/map_js.html' %}
     {% endcompress %}
   {% endblock %}

   {% block css %}
     {% compress css %}
       <link href="{% static 'vendors/maplibre/css/maplibre-gl.css' %}" rel='stylesheet'/>
     {% endcompress %}
   {% endblock css %}
   ```

7. If you want to integrate basemaps to your map add the following to the corresponding places:
   ```html
   <script src="{% static 'django_mapengine/js/basemaps.js' %}" type="text/javascript"></script>
   {% include 'django_mapengine/map_basemaps.html'}
   ```

# User Guides

- [How to define layers](docs/LAYERS.md)
- [How to enable popups](docs/POPUPS.md)
- [How to set up clusters](docs/CLUSTERS.md)
