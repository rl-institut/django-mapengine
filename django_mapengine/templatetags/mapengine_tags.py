"""Template tag to render one map (of possibly several) on a page."""

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from django_mapengine import maps

register = template.Library()

_SCRIPTS_INCLUDED_ATTR = "_mapengine_scripts_included"


@register.simple_tag(takes_context=True)
def mapengine_map(context, name: str = "default") -> str:
    """
    Render the container, setup/source JSON and store for one named map.

    The shared JS library files (django_mapengine/map_js.html) are only included once per
    request, no matter how many times this tag is used on the same page.

    Parameters
    ----------
    context : Context
        Template context; must contain the current request.
    name : str
        Name of the map to render (see 'MAP_ENGINE_MAPS' setting).

    Returns
    -------
    str
        Rendered HTML for this map.
    """
    request = context["request"]
    map_config = maps.get_map_config(name)
    map_context = maps.build_map_context(map_config, request)
    map_context["include_scripts"] = not getattr(request, _SCRIPTS_INCLUDED_ATTR, False)
    setattr(request, _SCRIPTS_INCLUDED_ATTR, True)
    return mark_safe(render_to_string("django_mapengine/map.html", map_context, request=request))  # noqa: S308
