
# Legend

To add a legend to your map, you have to include the following to your HTML containing the map:

- Add `<link rel="stylesheet" href="{% static 'django_mapengine/css/legend.css' %}" />` to your `<head>` section.
- Include legend via `{% include 'django_mapengine/legend.html' %}` above the map containing div (e.g. `{% mapengine_map "default" %}`).
- Note: The parent element of the legend must hold CSS attribute `position: relative` in order to place legend correctly.
- A legend belongs to exactly one map: build it with the same `map_name` as the `{% mapengine_map %}` call it sits next to (if you only have one map, the default `map_name="default"` is fine).

In the context of your view, add a legend (the `Legend` class allows for multiple initialization methods):

```python
from django.views.generic.base import TemplateView
from django_mapengine.legend import Legend


class MapView(TemplateView):
    """Render HTML for map."""

    template_name = "map.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["mapengine_legend"] = Legend.from_layer_names("Legende", ["fauna_flora_habitat"])
        return context
```

With multiple maps, pass `map_name` to scope the legend (and its default "checked" state, which
reflects that map's `layers_at_startup`) to the right map:

```python
context["mapengine_legend"] = Legend.from_layer_names("Legende", ["fauna_flora_habitat"], map_name="detail")
```
