
const defaultPaintProperties = ["fill-color", "fill-opacity"];

PubSub.subscribe(mapEvent.MAP_LAYERS_LOADED, initDefaultChoropleths);
PubSub.subscribe(mapEvent.CHOROPLETH_SELECTED, activateChoropleth);


function activateChoropleth(msg, choroplethName) {
  if (!(choroplethName in map_store.cold.choropleths)) {
    throw new ReferenceError(`Choropleth '${choroplethName}' unknown.`)
  }
  for (const layerID of map_store.cold.choropleths[choroplethName].layers) {
    if (!(layerID in map_store.cold.storedChoroplethPaintProperties[choroplethName])) {
      $.ajax({
        type: "GET",
        url: `choropleth/${choroplethName}/${layerID}`,
        data: map_store.cold.state,
        async: false,
        dataType: 'json',
        success: function (choroplethData) {
          if (map_store.cold.choropleths[choroplethName].useFeatureState) {
            updateChoroplethFeatureStates(choroplethName, layerID, choroplethData.values);
          }
          map_store.cold.storedChoroplethPaintProperties[choroplethName][layerID] = choroplethData.paintProperties;
          setPaintProperties(layerID, choroplethData.paintProperties);
        }
      });
    } else {
      setPaintProperties(layerID, map_store.cold.storedChoroplethPaintProperties[choroplethName][layerID]);
    }
  }
  map_store.cold.currentChoropleth = choroplethName;
  PubSub.publish(mapEvent.CHOROPLETH_UPDATED, choroplethName);
  legendElement.style.visibility = "visible";
  return logMessage(msg);
}

function updateChoroplethFeatureStates(choroplethName, layerID, featureStateValues) {
  for (var featureID in featureStateValues) {
    let choroplethFeatureState = map.getFeatureState(
      {
        source: layerID,
        sourceLayer: layerID,
        id: featureID,
      }
    );
    choroplethFeatureState[choroplethName] = featureStateValues[featureID];
    map.setFeatureState(
      {
        source: layerID,
        sourceLayer: layerID,
        id: featureID,
      },
      choroplethFeatureState
    );
  }
}

function initDefaultChoropleths() {
  for (const choropleth in map_store.cold.choropleths) {
    for (const layerID of map_store.cold.choropleths[choropleth].layers) {
      if (layerID in map_store.cold.storedChoroplethPaintProperties["default"]) continue;
      map_store.cold.storedChoroplethPaintProperties["default"][layerID] = getPaintProperties(layerID);
    }
  }
}

function deactivateChoropleth() {
  for (const choropleth in map_store.cold.choropleths) {
    for (const layerID of map_store.cold.choropleths[choropleth].layers) {
      setPaintProperties(layerID, map_store.cold.storedChoroplethPaintProperties["default"][layerID]);
    }
  }
  map_store.cold.currentChoropleth = null;
  legendElement.style.visibility = "hidden";
}

function setPaintProperties(layerID, paintProperties) {
  for (const property in paintProperties) {
    if (!(defaultPaintProperties.includes(property))) continue;
    map.setPaintProperty(layerID, property, paintProperties[property]);
  }
}

function getPaintProperties(layerID) {
  let paintProperties = {};
  for (const property of defaultPaintProperties) {
    paintProperties[property] = map.getPaintProperty(layerID, property);
  }
  return paintProperties;
}
