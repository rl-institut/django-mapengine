# Layers

## Add custom layer

To add a custom layer from an external source (e.g. vector, raster) you can use
the mapengine's `MapSource` which employs
[MapLibre's Source](https://maplibre.org/maplibre-gl-js/docs/API/interfaces/Source/).

In the following example, the WMS raster layer *Flurstücke* from
[ALKIS Brandenburg (WMS)](https://geoportal.brandenburg.de/detailansichtdienst/render?url=https://geoportal.brandenburg.de/gs-json/xml?fileid=31591bca-bb40-4d8a-98ad-35efc37524c9)
is added.

Adjust the tile URL to your needs, see the WMS GetCapabilities
([GetCapabilities for this example](https://isk.geobasis-bb.de/ows/alkis_wms?request=GetCapabilities&service=WMS))
for supported parameter values.

```
MAP_ENGINE_SOURCES = [
    setup.MapSource(
        name="wms_layer",
        type="raster",
        tiles=[
            "https://isk.geobasis-bb.de/ows/alkis_wms"
            "?bbox={bbox-epsg-3857}&format=image/png&service=WMS&version=1.3.0&request=GetMap&crs=EPSG:3857&"
            "styles&width=768&height=768&transparent=true&layers=adv_alkis_flurstuecke",
        ],
    ),
]

MAP_ENGINE_LAYERS = [
    setup.MapLayer(id="wms_layer", source="wms_layer", style={"type": "raster"}),
]
```

On WMS see also:
- [How to add WMS layer in MapLibre](https://maplibre.org/maplibre-gl-js/docs/examples/wms/)
- [WMS reference](https://docs.geoserver.org/stable/en/user/services/wms/reference.html)
- [OGC WMS standard](https://www.ogc.org/standard/wms/)

## Toggling layers
In your django project you can create inputs which get connected automatically connected to a layer in order to switch this layer on and off.
To do so, you have to create an `input` of `type` "checkbox" with an `id` which is related to layer ID you want to trigger:

```html
<input id="wind" type="checkbox">
```

Triggering (changing) this input will toggle all layers starting with "wind".
This guarantees that also clustered layers (in this example "wind", "wind_cluster" and "wind_cluster_count") are triggered.
