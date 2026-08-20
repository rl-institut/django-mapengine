
const defaultPaintProperties = ["fill-color", "fill-opacity"];

function setupChoroplethEvents(mapName, map, store) {
  PubSub.subscribe(mapEventTopic(mapName, mapEvent.MAP_LAYERS_LOADED), () => initDefaultChoropleths(map, store));
  PubSub.subscribe(
    mapEventTopic(mapName, mapEvent.CHOROPLETH_SELECTED),
    (msg, choroplethName) => activateChoropleth(mapName, map, store, msg, choroplethName)
  );
}


async function activateChoropleth(mapName, map, store, msg, choroplethName) {
  if (!(choroplethName in store.cold.choropleths)) {
    throw new ReferenceError(`Choropleth '${choroplethName}' unknown.`);
  }
  for (const layerID of store.cold.choropleths[choroplethName].layers) {
    const layerIDCleaned = layerID.endsWith("_distilled") ? layerID.slice(0, -10) : layerID;
    if (!(layerID in store.cold.storedChoroplethPaintProperties[choroplethName])) {
      const params = new URLSearchParams(store.cold.state);
      const response = await fetch(`choropleth/${choroplethName}/${layerIDCleaned}?${params}`);
      const choroplethData = await response.json();
      if (store.cold.choropleths[choroplethName].useFeatureState) {
        updateChoroplethFeatureStates(map, choroplethName, layerID, choroplethData.values);
      }
      store.cold.storedChoroplethPaintProperties[choroplethName][layerID] = choroplethData.paintProperties;
      setPaintProperties(map, layerID, choroplethData.paintProperties);
    } else {
      setPaintProperties(map, layerID, store.cold.storedChoroplethPaintProperties[choroplethName][layerID]);
    }
  }
  store.cold.currentChoropleth = choroplethName;
  PubSub.publish(mapEventTopic(mapName, mapEvent.CHOROPLETH_UPDATED), choroplethName);
  const legendElement = document.getElementById(`mapengine-legend-${mapName}`);
  if (legendElement) {
    legendElement.style.visibility = "visible";
  }
  return logMessage(mapName, msg);
}

function updateChoroplethFeatureStates(map, choroplethName, layerID, featureStateValues) {
  const layerIDCleaned = layerID.endsWith("_distilled") ? layerID.slice(0, -10) : layerID;
  for (var featureID in featureStateValues) {
    let choroplethFeatureState = map.getFeatureState(
      {
        source: layerID,
        sourceLayer: layerIDCleaned,
        id: featureID,
      }
    );
    choroplethFeatureState[choroplethName] = featureStateValues[featureID];
    map.setFeatureState(
      {
        source: layerID,
        sourceLayer: layerIDCleaned,
        id: featureID,
      },
      choroplethFeatureState
    );
  }
}

function initDefaultChoropleths(map, store) {
  for (const choropleth in store.cold.choropleths) {
    for (const layerID of store.cold.choropleths[choropleth].layers) {
      if (layerID in store.cold.storedChoroplethPaintProperties["default"]) continue;
      store.cold.storedChoroplethPaintProperties["default"][layerID] = getPaintProperties(map, layerID);
    }
  }
}

function deactivateChoropleth(mapName) {
  const {map, store} = MapEngine.maps[mapName];
  for (const choropleth in store.cold.choropleths) {
    for (const layerID of store.cold.choropleths[choropleth].layers) {
      setPaintProperties(map, layerID, store.cold.storedChoroplethPaintProperties["default"][layerID]);
    }
  }
  store.cold.currentChoropleth = null;
  const legendElement = document.getElementById(`mapengine-legend-${mapName}`);
  if (legendElement) {
    legendElement.style.visibility = "hidden";
  }
}

function setPaintProperties(map, layerID, paintProperties) {
  for (const property in paintProperties) {
    if (!(defaultPaintProperties.includes(property))) continue;
    map.setPaintProperty(layerID, property, paintProperties[property]);
  }
}

function getPaintProperties(map, layerID) {
  let paintProperties = {};
  for (const property of defaultPaintProperties) {
    paintProperties[property] = map.getPaintProperty(layerID, property);
  }
  return paintProperties;
}
