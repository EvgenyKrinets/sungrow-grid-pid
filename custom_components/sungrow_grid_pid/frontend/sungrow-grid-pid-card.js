const CARD_VERSION="3.0.6";

class SungrowGridPidCardEditor extends HTMLElement {
  set hass(h){ this._hass=h; if(!this._rendered) this._render(); }
  setConfig(c){
    this._config=c||{};
    if(!this._rendered) this._render();
    else this.querySelectorAll("select[data-k]").forEach(el=>{
      if(el!==document.activeElement && this._config[el.dataset.k] && el.value!==this._config[el.dataset.k])
        el.value=this._config[el.dataset.k];
    });
  }
  _render(){
    if(!this._hass) return;
    const cfg=this._config||{};
    const defaults={controller_entity:"automation.simple_grid_battery_controller",target_entity:"input_number.pid_grid_target",export_entity:"sensor.export_power",charge_entity:"number.battery_max_charge_power"};
    const options=(domain,key)=>Object.keys(this._hass.states)
      .filter(id=>id.startsWith(domain+"."))
      .map(id=>`<option value="${id}" ${(cfg[key]||defaults[key])===id?"selected":""}>${id} — ${this._hass.states[id].attributes.friendly_name||""}</option>`).join("");
    this.innerHTML=`
      <style>
        .row{margin:12px 0} label{display:block;font-weight:600;margin-bottom:5px}
        select{width:100%;padding:10px;border:1px solid var(--divider-color);border-radius:8px;background:var(--card-background-color);color:var(--primary-text-color)}
      </style>
      <div class="row"><label>PID Controller</label><select data-k="controller_entity"><option value="">По умолчанию: automation.simple_grid_battery_controller</option>${options("automation","controller_entity")}</select></div>
      <div class="row"><label>PID Grid Target</label><select data-k="target_entity"><option value="">По умолчанию: input_number.pid_grid_target</option>${options("input_number","target_entity")}</select></div>
      <div class="row"><label>Реальный экспорт</label><select data-k="export_entity"><option value="">sensor.export_power</option>${options("sensor","export_entity")}</select></div>
      <div class="row"><label>Задание зарядки батареи</label><select data-k="charge_entity"><option value="">number.battery_max_charge_power</option>${options("number","charge_entity")}</select></div>
    `;
    this._rendered=true;
    this.querySelectorAll("select").forEach(el=>el.onchange=()=>{
      this._config={...this._config,[el.dataset.k]:el.value||undefined};
      this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:this._config},bubbles:true,composed:true}));
    });
  }
}
if(customElements.get("sungrow-grid-pid-card-editor")) customElements.get("sungrow-grid-pid-card-editor").prototype.setConfig=SungrowGridPidCardEditor.prototype.setConfig;
else customElements.define("sungrow-grid-pid-card-editor",SungrowGridPidCardEditor);

class SungrowGridPidCard extends HTMLElement {
  static getStubConfig(){ return {}; }
  static getConfigElement(){ return document.createElement("sungrow-grid-pid-card-editor"); }

  constructor(){ super(); this.attachShadow({mode:"open"}); this._config={}; }
  setConfig(c){ this._config=c||{}; this._render(); }
  set hass(h){ this._hass=h; if(!this._dragging && !this._sending) this._render(); }
  getCardSize(){ return 3; }

  _find(domain,preferred,names=[],contains=[]){
    if(!this._hass) return null;
    if(preferred && this._hass.states[preferred]) return preferred;
    const states=Object.entries(this._hass.states).filter(([id])=>id.startsWith(domain+"."));
    for(const [id,s] of states){
      const f=String(s.attributes.friendly_name||"").trim().toLowerCase();
      if(names.some(n=>f===n.toLowerCase())) return id;
    }
    for(const [id,s] of states){
      const hay=(id+" "+String(s.attributes.friendly_name||"")).toLowerCase();
      if(contains.length && contains.every(k=>hay.includes(k))) return id;
    }
    return preferred||null;
  }

  _entities(){
    return {
      controller:this._find("automation",this._config.controller_entity||"automation.simple_grid_battery_controller",["Simple Grid Battery Controller"],["simple","grid","battery","controller"]),
      target:this._find("input_number",this._config.target_entity||"input_number.pid_grid_target",["PID Grid Target"],["pid","grid","target"]),
      exportPower:this._find("sensor",this._config.export_entity||"sensor.export_power",["Export Power"],["export","power"]),
      charge:this._find("number",this._config.charge_entity||"number.battery_max_charge_power",["Battery Max Charge Power"],["battery","charge","power"])
    };
  }

  _state(id,f="—"){ return id&&this._hass?.states[id]?this._hass.states[id].state:f; }
  _num(id){ const v=Number(this._state(id,NaN)); return Number.isFinite(v)?v:null; }
  _fmt(id){ const v=this._num(id); return v===null?"—":Math.round(v).toLocaleString()+" W"; }
  _more(id){ if(id) this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:id},bubbles:true,composed:true})); }
  _call(domain,service,data){ return this._hass?.callService(domain,service,data); }

  _render(){
    if(!this.shadowRoot || !this._hass) return;
    const e=this._entities();
    const on=this._state(e.controller)==="on";
    const controllerFound=!!(e.controller && this._hass.states[e.controller]);
    const foundAutomations=Object.entries(this._hass.states).filter(([id])=>id.startsWith("automation.") && (id.includes("grid")||id.includes("pid")||id.includes("battery")||id.includes("sungrow"))).map(([id])=>id);

    const targetState=e.target?this._hass.states[e.target]:null;
    const target=this._num(e.target)??15000;
    const min=Number(targetState?.attributes.min??0);
    const max=Number(targetState?.attributes.max??17000);
    const step=Number(targetState?.attributes.step??1000);

    this.shadowRoot.innerHTML=`
      <style>
        :host{display:block}*{box-sizing:border-box}
        ha-card{padding:14px 16px;border-radius:16px;background:var(--ha-card-background,var(--card-background-color,#fff));color:var(--primary-text-color)}
        .top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:10px}
        .title{font-size:18px;font-weight:700}.sub{font-size:12px;color:var(--secondary-text-color);margin-top:2px}
        .toggle{width:48px;height:28px;border:0;border-radius:16px;background:#b9c2cc;padding:3px;cursor:pointer}
        .toggle.on{background:#4b86b4}.knob{display:block;width:22px;height:22px;border-radius:50%;background:#fff;transition:.15s}.toggle.on .knob{transform:translateX(20px)}
        .target{cursor:pointer;padding:4px 0 2px}.targetHead{display:flex;justify-content:space-between;align-items:end;gap:10px}
        .targetName{font-size:14px}.targetValue{font-size:18px;font-weight:700}
        input[type=range]{width:100%;margin:10px 0 2px;accent-color:#4b86b4}
        .limits{display:flex;justify-content:space-between;font-size:10px;color:var(--secondary-text-color)}
        .stats{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
        .stat{border-top:1px solid var(--divider-color);padding-top:9px;cursor:pointer}.label{font-size:11px;color:var(--secondary-text-color)}.value{font-size:17px;font-weight:700;margin-top:3px}
        .missing{margin-top:10px;padding:8px;border-radius:8px;background:var(--warning-color,#f0ad4e22);font-size:11px}
      </style>
      <ha-card>
        <div class="top">
          <div><div class="title">PID Grid Target</div><div class="sub" id="pidStatus">Sungrow Grid PID v${CARD_VERSION} · ${on?"Running":"Stopped"}${controllerFound?"":" · automation not found"}</div></div>
          <button id="toggle" class="toggle ${on?"on":""}" ${controllerFound?"":"disabled"} title="${e.controller||"Automation not found"}"><span class="knob"></span></button>
        </div>

        <div class="target" id="targetInfo">
          <div class="targetHead"><span class="targetName">Целевой экспорт</span><span class="targetValue" id="targetValue">${Math.round(target).toLocaleString()} W</span></div>
          <input id="targetSlider" type="range" min="${min}" max="${max}" step="${step}" value="${Math.min(max,Math.max(min,target))}">
          <div class="limits"><span>${min.toLocaleString()} W</span><span>${max.toLocaleString()} W</span></div>
        </div>

        <div class="stats">
          <div class="stat" id="exportStat"><div class="label">Реальный экспорт</div><div class="value">${this._fmt(e.exportPower)}</div></div>
          <div class="stat" id="chargeStat"><div class="label">Задание зарядки батареи</div><div class="value">${this._fmt(e.charge)}</div></div>
        </div>

        ${(!controllerFound||!targetState)?'<div class="missing">Не найдена автоматизация или PID Grid Target. Автоматизации-кандидаты: ${foundAutomations.length?foundAutomations.join(", "):"нет"}. Проверьте YAML и настройки карточки.</div>':""}
      </ha-card>
    `;

    const slider=this.shadowRoot.getElementById("targetSlider");
    const value=this.shadowRoot.getElementById("targetValue");
    slider.onpointerdown=()=>{this._dragging=true;};
    slider.onpointerup=()=>{this._dragging=false;};
    slider.oninput=(ev)=>{ this._dragging=true; value.textContent=Math.round(Number(ev.target.value)).toLocaleString()+" W"; };
    slider.onchange=async(ev)=>{ this._dragging=false; if(!targetState)return; this._sending=true; try{await this._hass.callService("input_number","set_value",{entity_id:e.target,value:Number(ev.target.value)});}finally{this._sending=false;this._render();} };

    this.shadowRoot.getElementById("targetInfo").onclick=(ev)=>{
      if(ev.target===slider) return;
      this._more(e.target);
    };
    this.shadowRoot.getElementById("toggle").onclick=async()=>{
      if(!controllerFound)return;
      const btn=this.shadowRoot.getElementById("toggle");
      const status=this.shadowRoot.getElementById("pidStatus");
      btn.disabled=true;
      status.textContent="Sungrow Grid PID · "+(on?"Отключение...":"Включение...");
      try {
        await this._call("automation",on?"turn_off":"turn_on",{entity_id:e.controller,skip_condition:true});
        const actual=this._state(e.controller);
        status.textContent="Sungrow Grid PID · "+(actual==="on"?"Running":actual==="off"?"Stopped":"Статус: "+actual);
        if(actual!==(on?"off":"on"))status.textContent+=" · проверьте журнал Home Assistant";
      }catch(error){
        status.textContent="Ошибка PID: "+(error?.message||String(error));
        console.error("Sungrow Grid PID switch activation error",e.controller,error);
      }finally{btn.disabled=false;}
    };
    this.shadowRoot.getElementById("exportStat").onclick=()=>this._more(e.exportPower);
    this.shadowRoot.getElementById("chargeStat").onclick=()=>this._more(e.charge);
  }
}

if(customElements.get("sungrow-grid-pid-card")) {
  const old=customElements.get("sungrow-grid-pid-card").prototype;
  for(const name of Object.getOwnPropertyNames(SungrowGridPidCard.prototype)) {
    if(name!=="constructor") Object.defineProperty(old,name,Object.getOwnPropertyDescriptor(SungrowGridPidCard.prototype,name));
  }
} else customElements.define("sungrow-grid-pid-card",SungrowGridPidCard);
window.customCards=window.customCards||[];
if(!window.customCards.some(c=>c.type==="sungrow-grid-pid-card")){
  window.customCards.push({type:"sungrow-grid-pid-card",name:"Sungrow Grid PID",description:"Управление обычной PID-автоматизацией и input_number.pid_grid_target",preview:false,documentationURL:"https://github.com/EvgenyKrinets/sungrow-grid-pid"});
}
