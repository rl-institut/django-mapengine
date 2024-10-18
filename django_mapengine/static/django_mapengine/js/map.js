
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
