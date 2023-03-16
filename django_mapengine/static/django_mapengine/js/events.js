
const mapEvent = {
    MAP_LOADED: "MAP_LOADED",
    MAP_SOURCES_LOADED: "MAP_SOURCES_LOADED",
    MAP_LAYERS_LOADED: "MAP_LAYERS_LOADED",
};


function subscribeToEvents(eventsList, subscriberFunction) {
  Array.from(eventsList).forEach(event => {
    PubSub.subscribe(event, subscriberFunction);
  });
}