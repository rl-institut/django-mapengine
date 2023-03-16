// Variables

const detailLayers = Array.from(document.getElementsByClassName("static-layer"));
const layerInputClass = ".form-check-input";


// Event Handler

map.on("load", function () {
  // Layers Detail Panel
  detailLayers.map(layerForm => {
    layerForm.addEventListener("change", () => {
      PubSub.publish(eventTopics.DETAIL_LAYER_SWITCH_CLICK, {layerForm});
    });
  });
  $(".layer-setup").find(".js-slider").change(function() {
    const layerForm = $(this).closest("form");
    PubSub.publish(eventTopics.DETAIL_LAYER_SLIDER_CHANGE, {layerForm});
  });
  $(".layer-setup").find(".django-select2").change(function() {
    const layerForm = $(this).closest("form");
    PubSub.publish(eventTopics.DETAIL_LAYER_SELECT_CHANGE, {layerForm});
  });
});


// Subscriptions

// On Initial Load
PubSub.subscribe(eventTopics.STATES_INITIALIZED, hideDetailLayers);
PubSub.subscribe(mapEvent.MAP_SOURCES_LOADED, add_layers);

// Layers Detail Panel
PubSub.subscribe(eventTopics.DETAIL_LAYER_SWITCH_CLICK, checkLayerOfGivenLayerForm);
PubSub.subscribe(eventTopics.DETAIL_LAYER_SLIDER_CHANGE, filterChanged);
PubSub.subscribe(eventTopics.DETAIL_LAYER_SELECT_CHANGE, filterChanged);

// Subscriber Functions

function add_layers(msg)
{
  const layers = JSON.parse(document.getElementById("mapengine_layers").textContent);
  const layers_at_startup = JSON.parse(document.getElementById("mapengine_layers_at_startup").textContent);
  for (const layer of layers) {
    map.addLayer(layer);
    const isStartupLayer = layers_at_startup.some(startup_layer => layer.id.startsWith(startup_layer));
    if (isStartupLayer) {
      map.setLayoutProperty(layer.id, "visibility", "visible");
    } else {
      map.setLayoutProperty(layer.id, "visibility", "none");
    }

    if (map_store.cold.debug) {
      map.on("click", layer.id, function (e) {
        console.log(`${layer.id}:`, e.features[0].properties.name, e.features[0]);
      });
    }
  }
  PubSub.publish(mapEvent.MAP_LAYERS_LOADED);
  return logMessage(msg);
}

function hideDetailLayers(msg) {
  detailLayers.map(layer => {
    turn_off_layer(layer);
    $(layer).find(layerInputClass)[0].checked = false;
  });
  return logMessage(msg);
}

function showDetailLayers(msg) {
  for (let i = 0; i < detailLayers.length; i++) {
    $(detailLayers[i]).find(layerInputClass)[0].checked = (map_store.cold.staticState & 2 ** i) === 2 ** i;
    check_layer(detailLayers[i]);
  }
  return logMessage(msg);
}

function checkLayerOfGivenLayerForm(msg, {layerForm}) {
  check_layer(layerForm);
  map_store.cold.staticState = get_static_state();
  return logMessage(msg);
}

function setDetailLayersOnDetailLayersSwitchClick(msg) {
  detailLayers.map(layer => {
    turn_off_layer(layer);
    $(layer).find(layerInputClass)[0].checked = false;
  });
  map_store.cold.staticState = get_static_state();
  return logMessage(msg);
}

function filterChanged(msg, {layerForm}) {
  const layer_id = get_layer_id(layerForm);
  const filters = get_layer_filters(layerForm);
  const clustered = $(layerForm).hasClass("cluster-layer");
  const layers = map.getStyle().layers.filter(layer => layer.id.startsWith(layer_id));
  $.each(layers, function (i, layer) {
    set_filters(layer.id, filters, clustered);
  });
  return logMessage(msg);
}


// Helper Functions

function get_layer_id(layer_form) {
  return $(layer_form).find(layerInputClass)[0].id;
}

function check_layer(layer_form) {
  if ($(layer_form).find(layerInputClass)[0].checked) {
    const layer_id = get_layer_id(layer_form);
    const activated_layers = turn_on_layer(layer_form);
    const layers = map.getStyle().layers.filter(layer => layer.id.startsWith(layer_id));
    const deactivatedLayers = layers.filter(layer => !activated_layers.includes(layer.id));
    const waiting = () => {
      if (!map.isStyleLoaded()) {
        requestAnimationFrame(waiting);
      } else {
        $.each(deactivatedLayers, function (i, layer) {
          map.setLayoutProperty(layer.id, "visibility", "none");
        });
      }
    };
    waiting();
  } else {
    turn_off_layer(layer_form);
  }
}

function turn_off_layer(layer_form) {
  const layer_id = get_layer_id(layer_form);
  const layers = map.getStyle().layers.filter(layer => layer.id.startsWith(layer_id));
  $.each(layers, function (i, layer) {
    map.setLayoutProperty(layer.id, "visibility", "none");
  });
}

function turn_on_layer(layer_form) {
  const layer_id = get_layer_id(layer_form);
  const layers = map.getStyle().layers.filter(layer => layer.id.startsWith(layer_id));
  $.each(layers, function (i, layer) {
    map.setLayoutProperty(layer.id, "visibility", "visible");
  });
  return layers.map(layer => layer.id);
}

function get_layer_filters(layer_form) {
  let filters = [];

  // Add global region filters
  const layer_id = get_layer_id(layer_form);
  if (map_store.cold.region_filter_layers.includes(layer_id)) {
    const state = $("#id_state").val();
    if (state) {
        filters.push(
          {
            type: "value",
            name: "state_name",
            values: [state]
          }
        );
      }
    const district = $("#id_district").val();
    if (district) {
        filters.push(
          {
            type: "value",
            name: "district_name",
            values: [district]
          }
        );
      }
   }

  let sliders = $(layer_form).find(".js-slider");
  sliders.each(function (index, slider) {
    let filter_name = slider.id.slice(3);
    let result = $(slider).data("ionRangeSlider").result;
    filters.push(
      {
        type: "range",
        name: filter_name,
        from: result.from,
        to: result.to
      }
    );
  });

  let selects = $(layer_form).find(".django-select2");
  selects.each(function (index, select) {
    let filter_name = select.id.split("_").slice(0, -1).join("_");  // Remove layer name from filter name
    let result = $(select).val();
    if (result.length > 0) {
      filters.push(
        {
          type: "value",
          name: filter_name,
          values: result
        }
      );
    }
  });
  return filters;
}

function set_filters(layer, filters, clustered) {
  let map_filters = ["all"];

  const level = layer.split("_").at(-1);
  if (level in map_store.cold.zoom_levels) {
    // Cluster layer
    const cluster_filter = ["==", ["get", "zoom_level"], map_store.cold.zoom_levels[level][1]];
    map_filters.push(cluster_filter);
  } else {
    // Vector layer
    for (let i = 0; i < filters.length; i++) {
      if (filters[i].type == "range") {
        const lower_bound = [">=", ["get", filters[i].name], filters[i].from];
        const upper_bound = ["<=", ["get", filters[i].name], filters[i].to];
        map_filters.push(lower_bound);
        map_filters.push(upper_bound);
      }
      if (filters[i].type == "value") {
        const equals = ["match", ["get", filters[i].name], filters[i].values, true, false];
        map_filters.push(equals);
      }
    }
  }
  map.setFilter(layer, map_filters);
}
