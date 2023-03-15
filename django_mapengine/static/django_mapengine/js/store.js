class Store {
  constructor(cold_init, hot_init) {
    this.cold =cold_init || {};
    this.hot =hot_init || {};
  }

  set (key, value, silent=false) {
    const hasProp = this.hot.hasOwnProperty(key);
    if (!hasProp || this.hot[key] !== value) {
      // Store the value
      this.hot[key] = value;
      // Publish a topic asynchronously
      if (!silent) {
        PubSub.publish(key, value);
      }
      // Indicate success
      return true;
    }

    // Value already given
    return false;
  }
}

let store = new Store(store_cold_init, store_hot_init);
