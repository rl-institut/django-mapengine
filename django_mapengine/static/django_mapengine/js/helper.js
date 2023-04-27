// Global Helper Functions

function logMessage(msg) {
  if (map_store.cold.debugMode) {
    let caller = logMessage.caller;
    if (typeof caller === "function") {
      caller = caller.toString().substr("function ".length);
      caller = caller.substr(0, caller.indexOf("("));
    }
    const whatCalledWho = `${msg} triggered\n${caller}`;
    console.log(whatCalledWho);
    return whatCalledWho;
  }
}

function getLanguage() {
  // TODO: implement dynamic language determination
  // In the future this will properly be implement.
  // For now, this function always returns "en"
  return "en-US";
}
