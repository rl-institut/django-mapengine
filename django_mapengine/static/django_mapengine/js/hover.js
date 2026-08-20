
function setupHoverEvents(mapName, map, store) {
  PubSub.subscribe(mapEventTopic(mapName, mapEvent.MAP_LAYERS_LOADED), () => activate_hover_pointer(map, store));
  PubSub.subscribe(mapEventTopic(mapName, mapEvent.MAP_LAYERS_LOADED), () => activate_hovering(map, store));
}


function activate_hover_pointer(map, store) {
  for (const layer of store.cold.hover_layers) {
    // Show pointer cursor on fills
    map.on("mouseenter", layer, function () {
      map.getCanvas().style.cursor = "pointer";
    });
    map.on("mouseleave", layer, function () {
      map.getCanvas().style.cursor = "";
    });
  }
}

function activate_hovering(map, store) {
  store.cold.hoveredIds = {};
  for (const hover_layer of store.cold.hover_layers) {
    store.cold.hoveredIds[hover_layer] = 0;
    const layer = map.getLayer(hover_layer);
    // When the user moves their mouse over the fill layer, we'll update the
    // feature state for the feature under the mouse.
    map.on("mousemove", hover_layer, function (e) {
      if (e.features.length > 0) {
        if (store.cold.hoveredIds[hover_layer] >= 0) {
          // Fill layer
          map.setFeatureState({
            source: layer.source,
            sourceLayer: layer.sourceLayer,
            id: store.cold.hoveredIds[hover_layer]
          }, {
            hover: false
          });
        }
        store.cold.hoveredIds[hover_layer] = e.features[0].id;
        // Fill layer
        map.setFeatureState({
          source: layer.source,
          sourceLayer: layer.sourceLayer,
          id: store.cold.hoveredIds[hover_layer]
        }, {
          hover: true
        });
      }
    });

    // When the mouse leaves layer, update the feature state of the
    // previously hovered feature.
    map.on("mouseleave", hover_layer, function () {
      if (store.cold.hoveredIds[hover_layer] >= 0) {
        map.setFeatureState({
          source: layer.source,
          sourceLayer: layer.sourceLayer,
          id: store.cold.hoveredIds[hover_layer]
        }, {
          hover: false
        });
      }
      store.cold.hoveredIds[hover_layer] = 0;
    });
  }
}
