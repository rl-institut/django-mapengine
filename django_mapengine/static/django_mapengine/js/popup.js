
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
  if (!(layerID in map_store.cold.popups)) return false;
  if (map_store.cold.currentChoropleth === null) {
    return map_store.cold.popups[layerID].atDefaultLayer;
  } else {
    if (map_store.cold.popups[layerID].choropleths === null) return false;
    if (!map_store.cold.popups[layerID].choropleths.includes(map_store.cold.currentChoropleth)) return false;
  }
  return true;
}

function add_popups() {
  for (const popup in map_store.cold.popups) {
    add_popup(popup);
  }
}

function add_popup(layerID) {
  map.on("click", layerID, function (event) {
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
    const lookup = map_store.cold.currentChoropleth === null ? layerID : map_store.cold.currentChoropleth;

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
