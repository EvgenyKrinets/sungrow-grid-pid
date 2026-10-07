const CARD_VERSION = "1.1.0";

class SungrowGridPidCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
  }

  static getStubConfig() {
    return {};
  }

  setConfig(config) {
    this._config = config || {};
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 6;
  }

  _find(domain, preferred, names = [], contains = []) {
    if (!this._hass) return null;
    if (preferred && this._hass.states[preferred]) return preferred;
    const entries = Object.entries(this._hass.states).filter(([id]) => id.startsWith(domain + "."));
    for (const [id, st] of entries) {
      const friendly = String(st.attributes.friendly_name || "").toLowerCase();
      if (names.some((n) => friendly === n.toLowerCase())) return id;
    }
    for (const [id, st] of entries) {
      const hay = (id + " " + String(st.attributes.friendly_name || "")).toLowerCase();
      if (contains.every((x) => hay.includes(x))) return id;
    }
    return null;
  }

  _entities() {
    return {
      controller: this._find("switch", this._config.controller_entity, ["PID Grid Controller"], ["pid", "grid", "controller"]),
      target: this._find("number", this._config.target_entity, ["PID Grid Target"], ["pid", "grid", "target"]),
      output: this._find("sensor", this._config.output_entity, ["PID Output"], ["pid", "output"]),
      error: this._find("sensor", this._config.error_entity, ["PID Grid Error"], ["pid", "grid", "error"]),
      version: this._find("sensor", this._config.version_entity, ["Sungrow Grid PID Version"], ["grid", "pid", "version"]),
      exportPower: this._find("sensor", this._config.export_entity || "sensor.export_power", ["Export Power"], ["export", "power"]),
      chargePower: this._find("number", this._config.charge_entity || "number.battery_max_charge_power", ["Battery Max Charge Power"], ["charge", "power"]),
    };
  }

  _state(id, fallback = "—") {
    return id && this._hass?.states[id] ? this._hass.states[id].state : fallback;
  }

  _num(id) {
    const v = Number(this._state(id, NaN));
    return Number.isFinite(v) ? Math.round(v).toLocaleString() : "—";
  }

  _call(domain, service, data) {
    if (this._hass) this._hass.callService(domain, service, data);
  }

  _render() {
    if (!this.shadowRoot) return;
    const e = this._entities();
    const enabled = this._state(e.controller) === "on";
    const targetState = e.target && this._hass?.states[e.target];
    const target = Number(targetState?.state || 15000);
    const min = Number(targetState?.attributes.min ?? 0);
    const max = Number(targetState?.attributes.max ?? 25000);
    const step = Number(targetState?.attributes.step ?? 1000);

    this.shadowRoot.innerHTML = `
      <style>
        :host { display:block; }
        ha-card { padding: 18px; overflow:hidden; }
        .head { display:flex; align-items:center; justify-content:space-between; gap:16px; }
        .title { font-size:20px; font-weight:600; }
        .subtitle { color:var(--secondary-text-color); font-size:12px; margin-top:3px; }
        .switch { width:48px; height:28px; border-radius:16px; border:0; cursor:pointer; background:var(--divider-color); padding:3px; }
        .switch.on { background:var(--primary-color); }
        .knob { display:block; width:22px; height:22px; border-radius:50%; background:white; transition:.18s; box-shadow:0 1px 3px #0005; }
        .switch.on .knob { transform:translateX(20px); }
        .target { margin-top:20px; }
        .targetline { display:flex; justify-content:space-between; align-items:baseline; }
        .targetvalue { font-size:24px; font-weight:600; }
        input[type=range] { width:100%; margin:12px 0 2px; accent-color:var(--primary-color); }
        .limits { display:flex; justify-content:space-between; color:var(--secondary-text-color); font-size:11px; }
        .grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:18px; }
        .metric { background:var(--secondary-background-color); border-radius:12px; padding:12px; min-width:0; }
        .label { color:var(--secondary-text-color); font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .value { font-size:19px; font-weight:600; margin-top:5px; }
        .status { margin-top:14px; display:flex; justify-content:space-between; color:var(--secondary-text-color); font-size:12px; }
        .missing { margin-top:14px; color:var(--error-color); font-size:12px; }
      </style>
      <ha-card>
        <div class="head">
          <div><div class="title">Sungrow Grid PID</div><div class="subtitle">Grid export controller</div></div>
          <button class="switch ${enabled ? "on" : ""}" id="toggle" aria-label="PID Controller"><span class="knob"></span></button>
        </div>
        <div class="target">
          <div class="targetline"><span>Grid Target</span><span class="targetvalue">${Number.isFinite(target) ? Math.round(target).toLocaleString() : "—"} W</span></div>
          <input id="target" type="range" min="${min}" max="${max}" step="${step}" value="${target}" ${e.target ? "" : "disabled"}>
          <div class="limits"><span>${min.toLocaleString()} W</span><span>${max.toLocaleString()} W</span></div>
        </div>
        <div class="grid">
          <div class="metric"><div class="label">Grid Export</div><div class="value">${this._num(e.exportPower)} W</div></div>
          <div class="metric"><div class="label">PID Output</div><div class="value">${this._num(e.output)} W</div></div>
          <div class="metric"><div class="label">Grid Error</div><div class="value">${this._num(e.error)} W</div></div>
          <div class="metric"><div class="label">Battery Charge Command</div><div class="value">${this._num(e.chargePower)} W</div></div>
        </div>
        <div class="status"><span>Status: ${enabled ? "Running" : "Stopped"}</span><span>v${this._state(e.version, CARD_VERSION)}</span></div>
        ${(!e.controller || !e.target) ? '<div class="missing">PID entities not found. Add the Sungrow Grid PID integration in Settings → Devices & services.</div>' : ""}
      </ha-card>
    `;

    this.shadowRoot.getElementById("toggle")?.addEventListener("click", () => {
      if (!e.controller) return;
      this._call("switch", enabled ? "turn_off" : "turn_on", { entity_id: e.controller });
    });

    const slider = this.shadowRoot.getElementById("target");
    slider?.addEventListener("input", (ev) => {
      const out = this.shadowRoot.querySelector(".targetvalue");
      if (out) out.textContent = Math.round(Number(ev.target.value)).toLocaleString() + " W";
    });
    slider?.addEventListener("change", (ev) => {
      if (!e.target) return;
      this._call("number", "set_value", { entity_id: e.target, value: Number(ev.target.value) });
    });
  }
}

if (!customElements.get("sungrow-grid-pid-card")) {
  customElements.define("sungrow-grid-pid-card", SungrowGridPidCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((c) => c.type === "sungrow-grid-pid-card")) {
  window.customCards.push({
    type: "sungrow-grid-pid-card",
    name: "Sungrow Grid PID",
    description: "Control Sungrow grid export target and view PID status.",
    preview: true,
    documentationURL: "https://github.com/EvgenyKrinets/sungrow-grid-pid"
  });
}
