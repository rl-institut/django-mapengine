
PubSub.subscribe(eventTopics.MAP_LOADED, add_sources);
PubSub.subscribe(eventTopics.MAP_LOADED, add_satellite);


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
    const sources = JSON.parse(document.getElementById("map_sources").textContent);
    for (const source in sources) {
        map.addSource(source, sources[source]);
    }
    PubSub.publish(eventTopics.MAP_SOURCES_LOADED);
    return logMessage(msg);
}
