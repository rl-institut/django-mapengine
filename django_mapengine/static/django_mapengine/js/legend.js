const legendElement = document.getElementById("legend");

PubSub.subscribe(mapEvent.CHOROPLETH_UPDATED, loadLegend);

/**
 * Returns a legend HTML element as a string.
 *
 * Uses nextColumnStartIndex numeric value to determine
 * which legend item belongs in which of two columns
 *
 * @param {string} title - the title of the legend.
 * @param {string} unit - the unit name concerning the value range.
 * @param {Array<string>} colors - 6 hex (with #) or rgb(a) color values as string array.
 * @param {Array<string>} valueRanges - 6 value range strings as string array.
 * @param {number} nextColumnStartIndex - start index of item in the second column.
 * @return {string} - HTML element as a string.
 */
const createLegend = (title, unit, colors, valueRanges, nextColumnStartIndex = 3) => {
  return `
    <div class="legend__heading">
      <span class="legend__title">Legend -&nbsp;</span>
      <span class="legend__detail">${title}</span>
      <div class="legend__unit">(${unit})</div>
    </div>
    <div class="legend__wrap">
      <div class="legend__column">
        ${valueRanges.filter((value, idx) => idx < nextColumnStartIndex).map((value, idx) => `<div class="legend__item" id="legend__item__color-${idx}">${value}</div>`).join(' ')}
      </div>
      <div class="legend__column">
        ${valueRanges.filter((value, idx) => idx >= nextColumnStartIndex).map((value, idx) => `<div class="legend__item" id="legend__item__color-${idx + nextColumnStartIndex}">${value}</div>`).join(' ')}
      </div>
    </div>
    <style>
    ${colors.map((colorValue, idx) => ` #legend__item__color-${idx}:before { background-color: ${colorValue}; }`).join(' ')}
    </style>
  `;
};


function loadLegend(msg, choroplethName){
  const title = map_store.cold.choropleths[choroplethName]["name"];
  const unit = map_store.cold.choropleths[choroplethName]["unit"]; 
  const paintPropertiesPerLayer = map_store.cold.storedChoroplethPaintProperties[choroplethName];

  /* Find active layer */
  let paintProperties = null;
  for (const layerID in paintPropertiesPerLayer) {
    const layer = map.getLayer(layerID);
    if (map.getZoom() > layer.minzoom && map.getZoom() < layer.maxzoom){
      paintProperties = paintPropertiesPerLayer[layerID];
      break
    }
  }

  let colors = [];
  let values = [];

  for (const element in paintProperties["fill-color"]) {
    let current = paintProperties["fill-color"][element];

    if (typeof(current) == "number") {
      if (Number.isInteger(current) === false){
        current = current.toFixed(2);
      }

      if (values.length === 0) {
        values.push("0 - " + String(current));
      }
      else {
        values.push(values[values.length-1].split(" ").slice(-1)[0] + " - " + String(current));
      }
    }

    if (typeof(current) == "string" && current.slice(0,3) === "rgb") {
      colors.push(current);
    }
  }
  const entriesPerColumn = Math.floor(values.length / 2);
  legendElement.innerHTML = createLegend(title, unit, colors, values, entriesPerColumn);
  return logMessage(msg);
}
