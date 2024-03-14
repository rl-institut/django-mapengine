// Variables

const layerSwitches = Array.from(document.getElementsByClassName(map_store.cold.layer_switch_class));

// Event Handler

map.on("load", function () {
  layerSwitches.map(layerSwitch => {
    if (layerSwitch.type !== "checkbox") {
      console.warn(
        `Layer switch with id "${layerSwitch.id}" is not a checkbox 
        and cannot be connected to map layers automatically.`
      );
    } else {
      layerSwitch.addEventListener("change", () => {
        PubSub.publish(mapEvent.MAP_LAYER_SWITCH_CLICK, layerSwitch);
      });
    }
  });
});


// Subscriptions

PubSub.subscribe(mapEvent.MAP_SOURCES_LOADED, add_layers);
PubSub.subscribe(mapEvent.MAP_LAYER_SWITCH_CLICK, toggleLayer);


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

// Helper Functions

function turn_off_layer(layer_id) {
  const layers = map.getStyle().layers.filter(layer => layer.id.startsWith(layer_id));
  if (layers.length === 0) {
    throw new Error(`There are no layers starting with '${layer_id}' registered in map.`);
  }
  $.each(layers, function (i, layer) {
    map.setLayoutProperty(layer.id, "visibility", "none");
  });
}

function turn_on_layer(layer_id) {
  const layers = map.getStyle().layers.filter(layer => layer.id.startsWith(layer_id));
  if (layers.length === 0) {
    throw new Error(`There are no layers starting with '${layer_id}' registered in map.`);
  }
  $.each(layers, function (i, layer) {
    map.setLayoutProperty(layer.id, "visibility", "visible");
  });
  return layers.map(layer => layer.id);
}

function toggleLayer(msg, layerSwitch) {

  if (layerSwitch.checked) {
    turn_on_layer(layerSwitch.id);
  } else {
    turn_off_layer(layerSwitch.id);
  }
  return logMessage(msg);
}
