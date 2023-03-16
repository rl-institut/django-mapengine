const basemaps = ["satellite"];

function toggleBasemap(basemap) {
  map_store.cold.basemap = basemap;

  if (basemap === null) {
    map_store.cold.basemapFocusElement = "basemaps__default";
  } else {
    map_store.cold.basemapFocusElement = `basemaps__${basemap}`;
  }

  const legend = document.getElementById("legend");
  for (const bm of basemaps) {
    map.setLayoutProperty(bm, "visibility", "none");
  }
  if (basemap !== null) {
    map.setLayoutProperty(basemap, "visibility", "visible");
  }
  else {
    legend.hidden = true;

  }
}

// Toggle basemaps control
let toggleBasemapButton = document.getElementById("basemaps-control");

function toggleBasemapControl() {
  const basemapControl = document.getElementById("basemaps");

  if (basemapControl.style.display !== "none") {
    basemapControl.style.display = "none";
  }
  else {
    basemapControl.style.display = "flex";
    document.getElementById(map_store.cold.basemapFocusElement).focus();
  }
}

toggleBasemapButton.onclick = toggleBasemapControl;
