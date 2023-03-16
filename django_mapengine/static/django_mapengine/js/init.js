

const map_store = initStore();
const map = createMap();


function initStore() {
    const store_cold_init = JSON.parse(document.getElementById("mapengine_store_cold_init").textContent);
    return new Store(store_cold_init);
}