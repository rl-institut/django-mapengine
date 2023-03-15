
PubSub.subscribe(eventTopics.MAP_LOADED, activate_region_pointer);
PubSub.subscribe(eventTopics.MAP_LOADED, activate_region_hovering);


function activate_region_pointer() {
  for (const region_layer of store.cold.region_layers) {
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
  for (const region_layer of store.cold.region_layers) {
    const layer = map.getLayer("fill-municipality")
    // When the user moves their mouse over the fill layer, we'll update the
    // feature state for the feature under the mouse.
    map.on("mousemove", region_layer, function (e) {
      if (e.features.length > 0) {
        if (store.cold.hoveredStateId >= 0) {
          // Fill layer
          map.setFeatureState({
            source: layer.source,
            sourceLayer: layer.source_layer,
            id: store.cold.hoveredStateId
          }, {
            hover: false
          });
          // Label layer
          map.setFeatureState({
            source: layer.source,
            sourceLayer: `${layer.source_layer}label`,
            id: store.cold.hoveredStateId
          }, {
            hover: false
          });
        }
        store.cold.hoveredStateId = e.features[0].id;
        // Fill layer
        map.setFeatureState({
          source: layer.source,
          sourceLayer: layer.source_layer,
          id: store.cold.hoveredStateId
        }, {
          hover: true
        });
        // Label layer
        map.setFeatureState({
          source: layer.source,
          sourceLayer: `${layer.source_layer}label`,
          id: store.cold.hoveredStateId
        }, {
          hover: true
        });
      }
    });

    // When the mouse leaves the fill layer, update the feature state of the
    // previously hovered feature.
    map.on("mouseleave", region_layer, function () {
      if (store.cold.hoveredStateId >= 0) {
        map.setFeatureState({
          source: layer.source,
          sourceLayer: layer.source_layer,
          id: store.cold.hoveredStateId
        }, {
          hover: false
        });
      }
      store.cold.hoveredStateId = null;
    });
  }
}