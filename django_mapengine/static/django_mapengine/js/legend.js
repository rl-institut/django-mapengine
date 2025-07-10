
const layerSwitches = document.querySelectorAll('.mapengine-layer');
const legend   = document.getElementById('mapengine-legend');
const openBtn  = document.getElementById('mapengine-legend-open-btn');
const closeBtn = document.getElementById('mapengine-legend-close-btn');

closeBtn.addEventListener('click', () => {
  legend.classList.add('hidden');
  openBtn .classList.remove('hidden');
});

openBtn.addEventListener('click', () => {
  legend.classList.remove('hidden');
  openBtn .classList.add('hidden');
});

PubSub.subscribe(mapEvent.MAP_LAYER_SWITCH_CLICK, toggleLayer);

// Event Handler

map.on("load", function () {
  layerSwitches.forEach(layerSwitch => {
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

function toggleLayer(msg, layerSwitch) {
  const layerName = layerSwitch.getAttribute('data-layer-name');
  if (layerSwitch.checked) {
    turn_on_layer(layerName);
    if (map_store.cold.cluster_layers.includes(layerName)) {
      turn_on_layer(`${layerName}_cluster`);
      turn_on_layer(`${layerName}_cluster_count`);
    }
  } else {
    turn_off_layer(layerName);
    if (map_store.cold.cluster_layers.includes(layerName)) {
      turn_off_layer(`${layerName}_cluster`);
      turn_off_layer(`${layerName}_cluster_count`);
    }
  }
  return logMessage(msg);
}
