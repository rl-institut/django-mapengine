
let popupClicked = false;
const POPUP_DOUBLE_CLICK_TIMEOUT = 300;

PubSub.subscribe(mapEvent.MAP_SOURCES_LOADED, add_popups);


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

function checkPop(layerID) {
  // Check if layer allows popups
  if (!(layerID in map_store.cold.popups)) return false;
  // Always return true if layer allows popups per default
  if (map_store.cold.popups[layerID].atDefaultLayer) return true;

  // Otherwise only possible popup comes from choropleth - check it
  if (map_store.cold.currentChoropleth === null) return false;
  if (map_store.cold.popups[layerID].choropleths === null) return false;
  return map_store.cold.popups[layerID].choropleths.includes(map_store.cold.currentChoropleth);
}

function add_popups() {
  for (const popup in map_store.cold.popups) {
    add_popup(popup);
  }
}

function add_popup(layerID) {
  map.on("click", layerID, function (event) {
    if (popupClicked) return;
    popupClicked = true;
    setTimeout(function() {
      popupClicked = false;
    }, POPUP_DOUBLE_CLICK_TIMEOUT);
    /*
      Check if popup already exists
    */
    if ($('.mapboxgl-popup').length > 0) {
      return;
    }
    if (!checkPop(layerID)) return;
    /*
      Construct Coordinates From Event
    */
    const coordinates = createCoordinates(event);

    const featureID = event.features[0].properties.id;

    // Check if choropleth of current layer is clicked
    let lookup = layerID;
    if (
        (map_store.cold.currentChoropleth !== null) &&
        (map_store.cold.popups[layerID].choropleths !== null) &&
        map_store.cold.popups[layerID].choropleths.includes(map_store.cold.currentChoropleth)
    ) {
       lookup = map_store.cold.currentChoropleth;
    }

    $.ajax({
      type: "GET",
      url: `/popup/${lookup}/${featureID}?lang=en`,
      data: map_store.cold.state,
      dataType: 'json',
      success: function (data) {
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
      }
    });
  });
}

$(document).ready(function () {
  $('#js-intro-modal').modal('show');
});
