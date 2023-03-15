const results_tab = document.getElementById("panel_3_results_tab");
const result_views = document.getElementById("result_views");

results_tab.addEventListener("shown.bs.tab", () => {
  PubSub.publish(eventTopics.RESULTS_TAB_CLICKED);
});
result_views.addEventListener("change", () => {
  PubSub.publish(eventTopics.RESULT_VIEW_CHANGED);
});

PubSub.subscribe(eventTopics.RESULTS_TAB_CLICKED, loadResults);
PubSub.subscribe(eventTopics.RESULTS_TAB_CLICKED, changeResultView);
PubSub.subscribe(eventTopics.RESULT_VIEW_CHANGED, changeResultView);


function loadResults(msg) {
  map.setLayoutProperty("results", "visibility", "visible");
  return logMessage(msg);
}

function changeResultView(msg) {
  const view = result_views.value;
  if (!(view in store.cold.result_views)) {
    $.ajax({
      type: "GET",
      url: `choropleth/${view}/1`,
      dataType: 'json',
      success: function(results) {
        updateResultsLayer(view, results);
        map.setPaintProperty("results", "fill-color", results.fill_color);
        PubSub.publish(eventTopics.RESULT_VIEW_UPDATED);
      }
    });
  }
  else {
    map.setPaintProperty("results", "fill-color", store.cold.result_views[view]);
    PubSub.publish(eventTopics.RESULT_VIEW_UPDATED);
  }
  return logMessage(msg);
}

function updateResultsLayer(view, results) {
  for (var feature_id in results.values) {
    let result_feature_state = map.getFeatureState(
      {
        source: "results",
        sourceLayer: "results",
        id: feature_id,
      }
    );
    result_feature_state[view] = results.values[feature_id];
    map.setFeatureState(
      {
        source: "results",
        sourceLayer: "results",
        id: feature_id,
      },
      result_feature_state
    );
  }
  store.cold.result_views[view] = results.fill_color;
}
