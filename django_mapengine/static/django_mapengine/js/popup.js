
let popupClicked = false;
const POPUP_DOUBLE_CLICK_TIMEOUT = 300;

function setupPopupEvents(mapName, map, store) {
  PubSub.subscribe(mapEventTopic(mapName, mapEvent.MAP_SOURCES_LOADED), () => add_popups(map, store));
}


function createCoordinates(event) {
  if ("lat" in event.features[0].properties) {
    return [event.features[0].properties.lat, event.features[0].properties.lon];
  }
  return event.lngLat;
}

function createListByName(name, series) {
  let list = [];
  for (const item in series) {
    list.push(series[item][name]);
  }
  return list;
}

function checkPop(store, layerID) {
  // Check if layer allows popups
  if (!(layerID in store.cold.popups)) return false;
  // Always return true if layer allows popups per default
  if (store.cold.popups[layerID].atDefaultLayer) return true;

  // Otherwise only possible popup comes from choropleth - check it
  if (store.cold.currentChoropleth === null) return false;
  if (store.cold.popups[layerID].choropleths === null) return false;
  return store.cold.popups[layerID].choropleths.includes(store.cold.currentChoropleth);
}

function add_popups(map, store) {
  for (const popup in store.cold.popups) {
    add_popup(map, store, popup);
  }
}

function add_popup(map, store, layerID) {
  map.on("click", layerID, function (event) {
    if (popupClicked) return;
    popupClicked = true;
    setTimeout(function() {
      popupClicked = false;
    }, POPUP_DOUBLE_CLICK_TIMEOUT);
    /*
      Check if popup already exists
    */
    if (document.querySelector('.mapboxgl-popup') !== null) {
      return;
    }
    if (!checkPop(store, layerID)) return;
    /*
      Construct Coordinates From Event
    */
    const coordinates = createCoordinates(event);

    const featureID = event.features[0].properties.id;

    // Check if choropleth of current layer is clicked
    let lookup = layerID;
    if (
        (store.cold.currentChoropleth !== null) &&
        (store.cold.popups[layerID].choropleths !== null) &&
        store.cold.popups[layerID].choropleths.includes(store.cold.currentChoropleth)
    ) {
       lookup = store.cold.currentChoropleth;
    }

    const params = new URLSearchParams(store.cold.state);
    fetch(`/popup/${lookup}/${featureID}?lang=en&${params}`)
      .then((response) => response.json())
      .then((data) => {
        const popup = document.createElement('div');
        const {html} = data;
        popup.innerHTML = html;

        new maplibregl.Popup({
          // https://maplibre.org/maplibre-gl-js-docs/api/markers/#popup-parameters
          maxWidth: "280px",
        }).setLngLat(coordinates).setHTML(popup.innerHTML).addTo(map);

        if ("chart" in data) {
          // createChart function must be defined in project app (not in mapengine)
          createChart("js-popup__chart", data.chart);
        }
      });
  });
}
