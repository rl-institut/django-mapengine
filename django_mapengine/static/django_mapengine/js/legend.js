
function setupLegendEvents(mapName) {
  const legendElement = document.getElementById(`mapengine-legend-${mapName}`);
  const openBtn = document.getElementById(`mapengine-legend-open-btn-${mapName}`);
  const closeBtn = document.getElementById(`mapengine-legend-close-btn-${mapName}`);
  if (!legendElement || !openBtn || !closeBtn) {
    // This map has no legend rendered on the page.
    return;
  }

  closeBtn.addEventListener('click', () => {
    legendElement.hidden = true;
    openBtn.hidden = false;
  });

  openBtn.addEventListener('click', () => {
    legendElement.hidden = false;
    openBtn.hidden = true;
  });

  const layerSwitches = legendElement.querySelectorAll('.mapengine-layer');
  layerSwitches.forEach(layerSwitch => {
    if (layerSwitch.type !== "checkbox") {
      console.warn(
        `Layer switch with id "${layerSwitch.id}" is not a checkbox
        and cannot be connected to map layers automatically.`
      );
    } else {
      layerSwitch.addEventListener("change", () => {
        PubSub.publish(mapEventTopic(mapName, mapEvent.MAP_LAYER_SWITCH_CLICK), layerSwitch);
      });
    }
  });

  PubSub.subscribe(
    mapEventTopic(mapName, mapEvent.MAP_LAYER_SWITCH_CLICK),
    (msg, layerSwitch) => toggleLayer(mapName, msg, layerSwitch)
  );
}

function toggleLayer(mapName, msg, layerSwitch) {
  const store = MapEngine.maps[mapName].store;
  const layerName = layerSwitch.getAttribute('data-layer-name');
  if (layerSwitch.checked) {
    turn_on_layer(mapName, layerName);
    if (store.cold.cluster_layers.includes(layerName)) {
      turn_on_layer(mapName, `${layerName}_cluster`);
      turn_on_layer(mapName, `${layerName}_cluster_count`);
    }
  } else {
    turn_off_layer(mapName, layerName);
    if (store.cold.cluster_layers.includes(layerName)) {
      turn_off_layer(mapName, `${layerName}_cluster`);
      turn_off_layer(mapName, `${layerName}_cluster_count`);
    }
  }
  return logMessage(mapName, msg);
}
