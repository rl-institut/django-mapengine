
const mapEvent = {
    MAP_LOADED: "MAP_LOADED",
    MAP_SOURCES_LOADED: "MAP_SOURCES_LOADED",
    MAP_LAYERS_LOADED: "MAP_LAYERS_LOADED",
    MAP_LAYER_SWITCH_CLICK: "MAP_LAYER_SWITCH_CLICK",

    CHOROPLETH_SELECTED: "CHOROPLETH_SELECTED",
    CHOROPLETH_UPDATED: "CHOROPLETH_UPDATED",
};


function subscribeToEvents(eventsList, subscriberFunction) {
  Array.from(eventsList).forEach(event => {
    PubSub.subscribe(event, subscriberFunction);
  });
}