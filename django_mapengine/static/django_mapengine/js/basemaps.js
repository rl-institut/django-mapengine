
const toggleBasemapButton = document.getElementById("basemaps-control");
toggleBasemapButton.onclick = toggleBasemapControl;

const basemapButtons = document.getElementById("basemaps").querySelectorAll("button");
const basemaps = Array.from(basemapButtons).map(function (basemapButton) {return basemapButton.id.slice("basemaps__".length);});

for (const basemapButton of basemapButtons) {
  let basemap_layer = basemapButton.id.slice("basemaps__".length);
  basemapButton.addEventListener("click", () => {
    toggleBasemap(basemap_layer);
  });
}

function toggleBasemap(basemap) {
  map_store.cold.basemap = basemap;

  const legend = document.getElementById("legend");
  for (const bm of basemaps) {
    if (bm !== "default") {
      map.setLayoutProperty(bm, "visibility", "none");
    }
  }
  if (basemap !== "default") {
    map.setLayoutProperty(basemap, "visibility", "visible");
  }
  else {
    legend.hidden = true;
  }
}

function toggleBasemapControl() {
  const basemapControl = document.getElementById("basemaps");

  if (basemapControl.style.display !== "none") {
    basemapControl.style.display = "none";
  }
  else {
    basemapControl.style.display = "flex";
    document.getElementById(`basemaps__${map_store.cold.basemap}`).focus();
  }
}
