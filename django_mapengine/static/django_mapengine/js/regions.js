
PubSub.subscribe(mapEvent.MAP_LAYERS_LOADED, activate_region_pointer);
PubSub.subscribe(mapEvent.MAP_LAYERS_LOADED, activate_region_hovering);


function activate_region_pointer() {
  for (const region_layer of map_store.cold.regions) {
    // Show pointer cursor on fills
    map.on("mouseenter", region_layer, function () {
      map.getCanvas().style.cursor = "pointer";
    });
    map.on("mouseleave", region_layer, function () {
      map.getCanvas().style.cursor = "";
    });
  }
}

function activate_region_hovering() {
  for (const region_layer of map_store.cold.regions) {
    const layer = map.getLayer(region_layer);
    // When the user moves their mouse over the fill layer, we'll update the
    // feature state for the feature under the mouse.
    map.on("mousemove", region_layer, function (e) {
      if (e.features.length > 0) {
        if (map_store.cold.hoveredStateId >= 0) {
          // Fill layer
          map.setFeatureState({
            source: layer.source,
            sourceLayer: layer.source,
            id: map_store.cold.hoveredStateId
          }, {
            hover: false
          });
          // Label layer
          map.setFeatureState({
            source: layer.source,
            sourceLayer: `${layer.source}label`,
            id: map_store.cold.hoveredStateId
          }, {
            hover: false
          });
        }
        map_store.cold.hoveredStateId = e.features[0].id;
        // Fill layer
        map.setFeatureState({
          source: layer.source,
          sourceLayer: layer.source,
          id: map_store.cold.hoveredStateId
        }, {
          hover: true
        });
        // Label layer
        map.setFeatureState({
          source: layer.source,
          sourceLayer: `${layer.source}label`,
          id: map_store.cold.hoveredStateId
        }, {
          hover: true
        });
      }
    });

    // When the mouse leaves the fill layer, update the feature state of the
    // previously hovered feature.
    map.on("mouseleave", region_layer, function () {
      if (map_store.cold.hoveredStateId >= 0) {
        map.setFeatureState({
          source: layer.source,
          sourceLayer: layer.source,
          id: map_store.cold.hoveredStateId
        }, {
          hover: false
        });
        map.setFeatureState({
          source: layer.source,
          sourceLayer: `${layer.source}label`,
          id: map_store.cold.hoveredStateId
        }, {
          hover: false
        });
      }
      map_store.cold.hoveredStateId = null;
    });
  }
}