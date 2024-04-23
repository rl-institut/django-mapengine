
map.on("load", async function() {
  PubSub.publish(mapEvent.MAP_LOADED);
});

PubSub.subscribe(mapEvent.MAP_LOADED, add_sources);
PubSub.subscribe(mapEvent.MAP_LOADED, add_images);


function add_sources(msg) {
    const sources = JSON.parse(document.getElementById("mapengine_sources").textContent);
    for (const source in sources) {
        map.addSource(source, sources[source]);
    }
    PubSub.publish(mapEvent.MAP_SOURCES_LOADED);
    return logMessage(msg);
}

async function add_images(msg) {
    const map_images = JSON.parse(document.getElementById("mapengine_images").textContent);
    const version = (maplibregl.version === undefined) ? maplibregl.getVersion() : maplibregl.version;
    for (const map_image of map_images) {
        if (version < "3") {
            map.loadImage(map_image.path, function (error, image) {
                if (error) throw error;
                map.addImage(map_image.name, image);
            });
        } else {
            const image = await map.loadImage(map_image.path);
            map.addImage(map_image.name, image.data);
        }
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
    if (checkPop(features[i].layer.id)) {
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
