/* Regression: HA state updates must not destroy an open native time picker. */
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const cardPath = path.join(__dirname, "..", "custom_components", "sungrow_grid_pid", "frontend", "sungrow-grid-pid-card.js");
const classes = new Map();
const timeInput = {dataset: {time:"time.sem_morning_start"},value:"07:30"};
const nodes = new Map([
  ['[data-grid-state]',{textContent:"Stopped"}],
  ['[data-grid-status]',{textContent:"Stopped"}],
  ['[data-morning-status]',{textContent:"Not run yet"}],
  ['[data-stat="export"] b',{textContent:"0 W"}],
  ['[data-stat="charge"] b',{textContent:"0 W"}],
  ['[data-time]',timeInput],
]);
const makeSwitch = () => ({textContent:"START",classList:{toggle(){}}});
nodes.set('[data-switch="switch.sem_grid_target"]', makeSwitch());
nodes.set('[data-switch="switch.sem_morning_discharge"]', makeSwitch());
const root = {
  activeElement:null,
  querySelector(selector) {
    if(selector === "ha-card")return this.card;
    return nodes.get(selector) ?? null;
  },
  querySelectorAll(){return [];},
  set innerHTML(_) {throw Error("Native time-picker element was rebuilt");}
};
root.card={};
class BaseElement {
  attachShadow(){this.shadowRoot=root;}
}
const sandbox={
  HTMLElement:BaseElement,
  window:{customCards:[]},
  customElements:{
    get(name){return classes.get(name);},
    define(name,clazz){classes.set(name,clazz);}
  },
  CustomEvent:class {}
};
vm.runInNewContext(fs.readFileSync(cardPath,"utf8"), sandbox, {filename:cardPath});
const Card=classes.get("sungrow-grid-pid-card");
assert(Card,"Card registered");
const card=new Card();
card._config={};
const states = {
  "sensor.export_power":{state:"14000"},
  "number.battery_max_charge_power":{state:"2000"},
  "switch.sem_grid_target":{state:"on"},
  "switch.sem_morning_discharge":{state:"on"},
  "sensor.sem_manager_status":{state:"Grid Target active"},
  "sensor.sem_morning_discharge_status":{state:"Waiting"},
  "time.sem_morning_start":{state:"07:30:00"}
};
card.hass={states};
assert.equal(nodes.get('[data-grid-state]').textContent,"Active");
assert.equal(nodes.get('[data-stat="export"] b').textContent,"14,000 W");

// Simulate browser native time picker temporarily removing input focus.
card._timePickerEngaged=true;
root.activeElement=null;
timeInput.value="08:10"; // User's selection in progress (not yet saved).
for(let i=0;i<1000;i++){
  states["sensor.export_power"]={state:String(14000+i)};
  card.hass={states};
  assert.equal(root.querySelector("[data-time]"),timeInput);
  assert.equal(timeInput.value,"08:10","Must preserve the open picker's unsaved time");
}
assert.equal(nodes.get('[data-stat="export"] b').textContent,"14,999 W",
  "Power must still update while the picker is open");

// After selection is complete, an external HA time change should be reflected.
card._timePickerEngaged=false;
states["time.sem_morning_start"]={state:"08:10:00"};
card.hass={states};
assert.equal(timeInput.value,"08:10");

// A later HA update must not rebuild the card even when no control is active.
states["time.sem_morning_start"]={state:"08:45:00"};
card.hass={states};
assert.equal(timeInput.value,"08:45");
console.log("PASS: HA updates preserve native picker and continue live stat updates");
