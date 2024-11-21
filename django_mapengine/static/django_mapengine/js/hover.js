
PubSub.subscribe(mapEvent.MAP_LAYERS_LOADED, activate_hover_pointer);
PubSub.subscribe(mapEvent.MAP_LAYERS_LOADED, activate_hovering);


function activate_hover_pointer() {
  for (const layer of map_store.cold.hover_layers) {
    // Show pointer cursor on fills
    map.on("mouseenter", layer, function () {
      map.getCanvas().style.cursor = "pointer";
    });
    map.on("mouseleave", layer, function () {
      map.getCanvas().style.cursor = "";
    });
  }
}

function activate_hovering() {
  map_store.cold.hoveredIds = {};
  for (const hover_layer of map_store.cold.hover_layers) {
    map_store.cold.hoveredIds[hover_layer] = 0;
    const layer = map.getLayer(hover_layer);
    // When the user moves their mouse over the fill layer, we'll update the
    // feature state for the feature under the mouse.
    map.on("mousemove", hover_layer, function (e) {
      if (e.features.length > 0) {
        if (map_store.cold.hoveredIds[hover_layer] >= 0) {
          // Fill layer
          map.setFeatureState({
            source: layer.source,
            sourceLayer: layer.sourceLayer,
            id: map_store.cold.hoveredIds[hover_layer]
          }, {
            hover: false
          });
        }
        map_store.cold.hoveredIds[hover_layer] = e.features[0].id;
        // Fill layer
        map.setFeatureState({
          source: layer.source,
          sourceLayer: layer.sourceLayer,
          id: map_store.cold.hoveredIds[hover_layer]
        }, {
          hover: true
        });
      }
    });

    // When the mouse leaves layer, update the feature state of the
    // previously hovered feature.
    map.on("mouseleave", hover_layer, function () {
      if (map_store.cold.hoveredIds[hover_layer] >= 0) {
        map.setFeatureState({
          source: layer.source,
          sourceLayer: layer.source,
          id: map_store.cold.hoveredIds[hover_layer]
        }, {
          hover: false
        });
      }
      map_store.cold.hoveredIds[hover_layer] = 0;
    });
  }
}