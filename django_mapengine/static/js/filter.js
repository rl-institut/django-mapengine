const state_filter = $("#id_state");
const district_filter = $("#id_district");

const default_region_color = "rgb(250,174,29)";
const highlight_color = "red";

state_filter.on("change", function () {
  PubSub.publish(eventTopics.STATE_FILTER_CHANGE, state_filter.val());
});
district_filter.on("change", function () {
  PubSub.publish(eventTopics.DISTRICT_FILTER_CHANGE, district_filter.val());
});

PubSub.subscribe(eventTopics.STATE_FILTER_CHANGE, activate_state);
PubSub.subscribe(eventTopics.STATE_FILTER_CHANGE, change_region_filter);
PubSub.subscribe(eventTopics.DISTRICT_FILTER_CHANGE, activate_district);
PubSub.subscribe(eventTopics.DISTRICT_FILTER_CHANGE, change_region_filter);


function activate_state(msg, state, fly_to=true, async=true) {
  highlight_region("state", state);
  if (!state) {
    district_filter.prop("disabled", true);
    return logMessage(msg);
  }
  $.ajax({
    type: "GET",
    url: "state",
    dataType: 'json',
    async: async,
    data: {"state": state},
    success: function(results) {
      if (fly_to) {
        map.flyTo(
          {
            center: results.center,
            zoom: store.cold.zoom_levels.state[0],
            speed: 0.5
          }
        );
      }

      district_filter.find('option').remove().end();
      district_filter.append(
          $('<option>', {
            value: '',
            text : 'Select District'
          })
        );
      $.each(results.districts, function (i, district) {
        district_filter.append(
          $('<option>', {
            value: district,
            text : district
          })
        );
      });
      district_filter.prop("disabled", false);
    }
  });
  return logMessage(msg);
}

function activate_district(msg, district) {
  highlight_region("district", district);
  if (!district) {
    return logMessage(msg);
  }
  $.ajax({
    type: "GET",
    url: "district",
    dataType: 'json',
    data: {"district": district},
    success: function(results) {
      map.flyTo(
        {
          center: results.center,
          zoom: store.cold.zoom_levels.district[0],
          speed: 0.5
        }
      );
    }
  });
  return logMessage(msg);
}

function change_region_filter(msg) {
  $.each(detailLayers, function(i, layerForm) {
    let layer_id = get_layer_id(layerForm);
    if (store.cold.region_filter_layers.includes(layer_id)) {
      PubSub.publish(eventTopics.DETAIL_LAYER_SELECT_CHANGE, {layerForm});
    }
  });
  return logMessage(msg);
}

function highlight_region(region, name) {
  let paint_property;
  if (name) {
    paint_property = {
      "property": "name",
      "type": "categorical",
      "stops": [[name, highlight_color]],
      "default": default_region_color
    };
  } else {
    paint_property = default_region_color;
  }
  map.setPaintProperty("fill-" + region, "fill-color", paint_property);
}
