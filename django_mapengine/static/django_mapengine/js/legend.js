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
      <div class="legend__unit">${unit ? `(${unit})` : ""}</div>
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
  const title = map_store.cold.choropleths[choroplethName].title;
  const unit = map_store.cold.choropleths[choroplethName].unit;
  const paintPropertiesPerLayer = map_store.cold.storedChoroplethPaintProperties[choroplethName];

  /* Find active layer */
  let paintProperties = null;
  for (const layerID in paintPropertiesPerLayer) {
    const layer = map.getLayer(layerID);
    if (layer.visibility === "visible"){
      paintProperties = paintPropertiesPerLayer[layerID];
      break;
    }
  }
  if (paintProperties === null) {
    return logMessage(msg);
  }

  // Get array of colors in RGB format (i.e. "rgb(red, green, blue)")
  const colors_without_opacity = paintProperties["fill-color"].slice(3).filter((_, index) => index % 2 !== 0);
  const opacity = "fill-opacity" in paintProperties ? paintProperties["fill-opacity"] : 1;
  const colors = colors_without_opacity.map(rgb_color => rgb_color.slice(0, -1) + `, ${opacity})`);
  const values = paintProperties["fill-color"].slice(3).filter((_, index) => (index + 1) % 2 !== 0).map(value => value < 100 ? value.toFixed(2) : Math.round(value));


  // Use user labels if given
  let valueRanges = [];
  if (map_store.cold.choropleths[choroplethName].labels !== undefined) {
    valueRanges = map_store.cold.choropleths[choroplethName].labels;
  } else {
    const step_size = parseFloat(values[1]) - parseFloat(values[0]);
    for (let i = 0; i < values.length; i++) {
      const nextValue = i === values.length - 1 ? Math.round(parseFloat(values[i]) + step_size) : values[i + 1];
      valueRanges.push(`${values[i]} - ${nextValue}`);
    }
  }

  const entriesPerColumn = Math.floor(valueRanges.length / 2);
  console.log(entriesPerColumn)
  legendElement.innerHTML = createLegend(title, unit, colors, valueRanges, entriesPerColumn);
  return logMessage(msg);
}
