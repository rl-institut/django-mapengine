
function createMap() {
    return new maplibregl.Map({
        container: "map",
        style: "https://api.maptiler.com/maps/{{tiling_service_style_id}}/style.json?key={{tiling_service_token}}", // stylesheet location
        center: [10.407237624103573, 51.22757621251938], // starting position [lng, lat]
        zoom: 5.546712433728557, // starting zoom
        maxBounds: [[-2.54, 46.35], [23.93, 55.87]] // [[south-west], [north-east]] restrict area
    });
}

const map = createMap();

map.on("load", function () {
  PubSub.publish(eventTopics.MAP_LOADED);
});

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
