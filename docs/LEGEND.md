
# Legend

To add a legend to your map, you have to include the following to your HTML containing the map:

- Add `<link rel="stylesheet" href="{% static 'django_mapengine/css/legend.css' %}" />` to your `<head>` section.
- Include legend via `{% include 'django_mapengine/legend.html' %}` above the map containing div `<div id="map"></div>`.
- Add `<script src="{% static 'django_mapengine/js/legend.js' %}"></script>` after setup of the map via `{% include 'django_mapengine/map_js.html' %}`. 
