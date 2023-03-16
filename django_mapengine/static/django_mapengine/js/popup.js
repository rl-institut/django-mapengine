
PubSub.subscribe(mapEvent.MAP_SOURCES_LOADED, add_popups);


async function fetchGetJson(url) {
  try {
    // Default options are marked with *
    const response = await fetch(url, {
      method: "GET", // *GET, POST, PUT, DELETE, etc.
      mode: "cors", // no-cors, *cors, same-origin
      cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
      credentials: "same-origin", // include, *same-origin, omit
      headers: {
        "Content-Type": "application/json",
      }, redirect: "follow", // manual, *follow, error
      referrerPolicy: "no-referrer", // no-referrer, *client
    });
    return await response.json(); // parses JSON response into native JavaScript objects
  } catch (err) {
    if (err instanceof Error) {
      throw new Error(err.message);
    }
    throw err;
  }
}

function createCoordinates(event) {
  if ("lat" in event.features[0].properties) {
    return [event.features[0].properties.lat, event.features[0].properties.lon];
  }
  return event.lngLat;
}

function createListByName(name, series) {
  let list = [];
  for (const item in series) {
    list.push(series[item][name]);
  }
  return list;
}

function add_popups() {
  const popups = JSON.parse(document.getElementById("mapengine_popups").textContent);
  for (const popup of popups) {
    add_popup(popup);
  }
}

function add_popup(layer_id) {
  map.on("click", layer_id, function (event) {
    /*
      Check if popup already exists
    */
    if ($('.mapboxgl-popup').length > 0) {
      return;
    }

    /*
      Construct Coordinates From Event
    */
    const coordinates = createCoordinates(event);

    const region_id = event.features[0].properties.id;
    const lookup = document.getElementById('result_views').value;
    const url = `/popup/${lookup}/${region_id}?lang=en`;

    fetchGetJson(url).then(
      (response) => {
        const popup = document.createElement('div');
        const {html} = response;
        popup.innerHTML = html;

        if ("chart" in response) {
          // Chart Title
          const {chart: {title}} = response;

          // Chart
          const chartElement = popup.querySelector("#js-popup__chart");
          const chart = echarts.init(chartElement, null, {renderer: 'svg'});
          // TODO: use lookup property in payload to construct chart dynamically. For now we assume bar chart type.
          // TODO: In this fetch we always expect one payload item. Make failsafe.
          const {chart: {series}} = response;
          const xAxisData = createListByName("key", series[0].data);
          const yAxisData = createListByName("value", series[0].data);
          const option = {
            title: {
              text: title,
              textStyle: {
                color: '#002E50',
                fontSize: 14,
                fontWeight: 400,
                lineHeight: 16
              },
              left: 'center'
            },
            animation: false,
            tooltip: {
              trigger: 'axis',
              axisPointer: {
                type: 'shadow'
              }
            },
            grid: {
              left: 16,
              right: 0,
              bottom: 32,
              top: 48,
              containLabel: true
            },
            textStyle: {
              color: '#002E50'
            },
            xAxis: [{
              type: 'category',
              data: xAxisData,
              axisTick: {
                show: false
              },
              axisLine: {
                show: true,
                lineStyle: {
                  color: '#ECF2F6'
                }
              },
            }],
            yAxis: [{
              type: 'value',
              splitLine: {
                show: true,
                lineStyle: {
                  color: '#ECF2F6'
                }
              }
            }],
            series: [{
              name: 'Direct',
              type: 'line',
              symbol: 'circle',
              symbolSize: 6,
              data: yAxisData,
              lineStyle: {
                color: '#002E50'
              },
              itemStyle: {
                color: '#002E50'
              }
            }]
          };
          chart.setOption(option);
        }

        requestAnimationFrame(() => {
            new maplibregl.Popup({
              // https://maplibre.org/maplibre-gl-js-docs/api/markers/#popup-parameters
              maxWidth: "280px",
            }).setLngLat(coordinates).setHTML(popup.innerHTML).addTo(map);
          });
      });
  });
}

$(document).ready(function () {
  $('#js-intro-modal').modal('show');
});
