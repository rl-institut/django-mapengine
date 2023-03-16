
map.on("load", function () {
  PubSub.publish(mapEvent.MAP_LOADED);
});

PubSub.subscribe(mapEvent.MAP_LOADED, add_sources);
PubSub.subscribe(mapEvent.MAP_LOADED, add_satellite);
PubSub.subscribe(mapEvent.MAP_LOADED, add_images);


function add_satellite(msg) {
    const layers = map.getStyle().layers;
    // Find the index of the first symbol layer in the map style
    let firstSymbolId;
    for (let i = 0; i < layers.length; i++) {
        if (layers[i].type === "symbol") {
            firstSymbolId = layers[i].id;
            break;
        }
    }
    map.addLayer(
        {
            id: "satellite",
            type: "raster",
            source: "satellite"
        },
        firstSymbolId
    );
    map.setLayoutProperty("satellite", "visibility", "none");
    return logMessage(msg);
}

function add_sources(msg) {
    const sources = JSON.parse(document.getElementById("mapengine_sources").textContent);
    for (const source in sources) {
        map.addSource(source, sources[source]);
    }
    PubSub.publish(mapEvent.MAP_SOURCES_LOADED);
    return logMessage(msg);
}

function add_images(msg) {
    const map_images = JSON.parse(document.getElementById("mapengine_images").textContent);
    for (const map_image of map_images) {
        map.loadImage(map_image.path, function (error, image) {
            if (error) throw error;
            map.addImage(map_image.name, image);
        });
    }
}

// Fly to level of detail of clicked on feature
function flyToElement(element) {
  const features = map.queryRenderedFeatures(element.point);
  let region = null;
  for (let i = 0; i < features.length; i++) {
    if (map_store.cold.regions.includes(features[i].layer.id)) {
      region = features[i];
    }
    if (map_store.cold.popup_layers.includes(features[i].layer.id)) {
      return;
    }
  }

  // Zoom to region
  if (region == null) {
    return;
  }

  // Get zoom-to level
  let zoom = (region.layer.maxzoom < 11) ? region.layer.maxzoom : 11;

  // Fly to center of bounding box and zoom to max zoom of layer
  map.flyTo({
    center: element.lngLat,
    zoom: zoom,
    essential: true
  });
}
