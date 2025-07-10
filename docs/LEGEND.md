
# Legend

To add a legend to your map, you have to include the following to your HTML containing the map:

- Add `<link rel="stylesheet" href="{% static 'django_mapengine/css/legend.css' %}" />` to your `<head>` section.
- Include legend via `{% include 'django_mapengine/legend.html' %}` above the map containing div `<div id="map"></div>`.
- Add `<script src="{% static 'django_mapengine/js/legend.js' %}"></script>` after setup of the map via `{% include 'django_mapengine/map_js.html' %}`. 

In the Context of your view, you can now add a legend (the `Legend` class allows for multiple initialization methods):

```python
from django.views.generic.base import TemplateView
from django_mapengine.views import MapEngineMixin
from django_mapengine.legend import Legend


class MapView(TemplateView, MapEngineMixin):
    """Render HTML for map."""

    template_name = "map.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["mapengine_legend"] = Legend.from_layer_names("Legende", ["fauna_flora_habitat"])
        return context
```
