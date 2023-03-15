// Disable zoom on double click
map.doubleClickZoom.disable();

// Fly to level of detail of clicked on feature
function flyToElement(element) {
  const features = map.queryRenderedFeatures(element.point);
  let region = null;
  for (let i = 0; i < features.length; i++) {
    if (store.cold.region_layers.includes(features[i].layer.id)) {
      region = features[i];
    }
    if (store.cold.popup_layers.includes(features[i].layer.id)) {
      return;
    }
  }

  // Zoom to region
  if (region == null) {
    return;
  }
  if (region.source == "state") {
    state_filter.val(region.properties.name);
    PubSub.publish(eventTopics.STATE_FILTER_CHANGE, state_filter.val());
  } else if (region.source == "district") {
    state_filter.val(region.properties.state_name);
    activate_state(eventTopics.STATE_FILTER_CHANGE, state_filter.val(), false, false);
    district_filter.val(region.properties.name);
    PubSub.publish(eventTopics.DISTRICT_FILTER_CHANGE, region.properties.name);
  } else {
    // Get zoom-to level
    let zoom = (region.layer.maxzoom < 11) ? region.layer.maxzoom : 11;

    // Fly to center of bounding box and zoom to max zoom of layer
    map.flyTo({
      center: element.lngLat,
      zoom: zoom,
      essential: true
    });
  }
}

function toggleSatellite() {
  if (map.getLayoutProperty("satellite", "visibility") == "none") {
    map.setLayoutProperty("satellite", "visibility", "visible");
  } else {
    map.setLayoutProperty("satellite", "visibility", "none");
  }
}
