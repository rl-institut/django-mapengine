
const basemapsByMap = new Map();

function setupBasemapEvents(mapName) {
  const toggleBasemapButton = document.getElementById(`basemaps-control-${mapName}`);
  const basemapControl = document.getElementById(`basemaps-${mapName}`);
  if (!toggleBasemapButton || !basemapControl) {
    // This map has no basemap switcher rendered on the page.
    return;
  }

  const prefix = "basemaps__";
  const suffix = `-${mapName}`;
  const basemapButtons = basemapControl.querySelectorAll("button");
  const basemaps = Array.from(basemapButtons).map(
    (basemapButton) => basemapButton.id.slice(prefix.length, -suffix.length)
  );
  basemapsByMap.set(mapName, basemaps);

  toggleBasemapButton.onclick = () => toggleBasemapControl(mapName);

  for (const basemapButton of basemapButtons) {
    const basemap_layer = basemapButton.id.slice(prefix.length, -suffix.length);
    basemapButton.addEventListener("click", () => {
      activateBasemap(mapName, basemap_layer);
    });
  }
}

function activateBasemap(mapName, basemap) {
  const {map, store} = MapEngine.maps[mapName];
  store.cold.basemap = basemap;

  for (const bm of basemapsByMap.get(mapName)) {
    if (bm !== "default") {
      map.setLayoutProperty(bm, "visibility", "none");
    }
  }
  if (basemap !== "default") {
    map.setLayoutProperty(basemap, "visibility", "visible");
  } else {
    const legendElement = document.getElementById(`mapengine-legend-${mapName}`);
    if (legendElement) {
      legendElement.hidden = true;
    }
  }
}

function toggleBasemapControl(mapName) {
  const basemapControl = document.getElementById(`basemaps-${mapName}`);

  if (basemapControl.style.display !== "none") {
    basemapControl.style.display = "none";
  }
  else {
    basemapControl.style.display = "flex";
    const store = MapEngine.maps[mapName].store;
    document.getElementById(`basemaps__${store.cold.basemap}-${mapName}`).focus();
  }
}
