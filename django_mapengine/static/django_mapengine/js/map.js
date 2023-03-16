
const map = createMap();
add_images();

map.on("load", function () {
  PubSub.publish(eventTopics.MAP_LOADED);
});

PubSub.subscribe(eventTopics.MAP_LOADED, add_sources);
PubSub.subscribe(eventTopics.MAP_LOADED, add_satellite);


function createMap() {
    const setup = JSON.parse(document.getElementById("mapengine_setup").textContent);
    const map = new maplibregl.Map(setup);

    if (store.cold.debugMode) {
        map.showTileBoundaries = true;
      }

    // Disable zoom on double click
    map.doubleClickZoom.disable();

    // Zoom to feature on click
      map.on("click", function (element) {
        flyToElement(element);
      });

    const nav = new maplibregl.NavigationControl();
    map.addControl(nav, "bottom-left");
    map.addControl(new maplibregl.ScaleControl({position: 'bottom-right'}));
    return map;
}

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
    PubSub.publish(eventTopics.MAP_SOURCES_LOADED);
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
    if (store.cold.region_layers.includes(features[i].layer.id)) {
      region = features[i];
    }
    if (store.cold.popup_layers.includes(features[i].layer.id)) {
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
