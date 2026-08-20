
window.MapEngine = window.MapEngine || {maps: {}};

MapEngine.init = function (mapName) {
    const store = initMapStore(mapName);
    const map = initMap(mapName, store);
    MapEngine.maps[mapName] = {map: map, store: store};

    setupMapEvents(mapName, map);
    setupLayerEvents(mapName, map, store);
    setupHoverEvents(mapName, map, store);
    setupPopupEvents(mapName, map, store);
    setupChoroplethEvents(mapName, map, store);
    setupLegendEvents(mapName);
    setupBasemapEvents(mapName);

    return MapEngine.maps[mapName];
};


function initMap(mapName, store) {
    const setup = JSON.parse(document.getElementById(`mapengine_setup_${mapName}`).textContent);
    const map = new maplibregl.Map(setup);

    if (store.cold.debugMode) {
        map.showTileBoundaries = true;
    }

    // Disable zoom on double click
    map.doubleClickZoom.disable();

    const nav = new maplibregl.NavigationControl();
    map.addControl(nav, "bottom-left");
    map.addControl(new maplibregl.ScaleControl({position: 'bottom-right'}));
    return map;
}


function initMapStore(mapName) {
    const storeColdInit = JSON.parse(document.getElementById(`mapengine_store_cold_init_${mapName}`).textContent);
    storeColdInit.state = {};
    storeColdInit.storedChoroplethPaintProperties = {"default": {}};
    for (const choroplethName in storeColdInit.choropleths) {
        storeColdInit.storedChoroplethPaintProperties[choroplethName] = {};
    }
    storeColdInit.currentChoropleth = null;
    return new Store(storeColdInit);
}
