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

```python
MAP_ENGINE_SOURCES = [
    setup.MapSource(
        name="bb_flurstuecke",
        type="raster",
        tiles=[
            "https://isk.geobasis-bb.de/ows/alkis_wms"
            "?bbox={bbox-epsg-3857}&format=image/png&service=WMS&version=1.3.0&request=GetMap&crs=EPSG:3857&"
            "styles&width=768&height=768&transparent=true&layers=adv_alkis_flurstuecke",
        ],
    ),
]

MAP_ENGINE_LAYERS = [
    setup.MapLayer(id="bb_flurstuecke", source="bb_flurstuecke", style={"type": "raster"}),
]
```

You will also need a style definition for the layer in your layer-style JSON file, e.g.
```json
{
    "bb_flurstuecke": {
        "type": "fill",
        "paint": {
            "fill-color": "#000000",
            "fill-opacity": 0.8
        }
    }
}
```

On WMS see also:
- [How to add WMS layer in MapLibre](https://maplibre.org/maplibre-gl-js/docs/examples/wms/)
- [WMS reference](https://docs.geoserver.org/stable/en/user/services/wms/reference.html)
- [OGC WMS standard](https://www.ogc.org/standard/wms/)
