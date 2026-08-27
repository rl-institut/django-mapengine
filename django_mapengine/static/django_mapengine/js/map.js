
function setupMapEvents(mapName, map) {
  map.on("load", function() {
    PubSub.publish(mapEventTopic(mapName, mapEvent.MAP_LOADED));
  });

  PubSub.subscribe(mapEventTopic(mapName, mapEvent.MAP_LOADED), (msg) => add_sources(mapName, map, msg));
  PubSub.subscribe(mapEventTopic(mapName, mapEvent.MAP_LOADED), (msg) => add_images(mapName, map, msg));
}


function add_sources(mapName, map, msg) {
    const sources = JSON.parse(document.getElementById(`mapengine_sources_${mapName}`).textContent);
    for (const source in sources) {
        map.addSource(source, sources[source]);
    }
    PubSub.publish(mapEventTopic(mapName, mapEvent.MAP_SOURCES_LOADED));
    return logMessage(mapName, msg);
}

async function add_images(mapName, map, msg) {
    const map_images = JSON.parse(document.getElementById(`mapengine_images_${mapName}`).textContent);
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
