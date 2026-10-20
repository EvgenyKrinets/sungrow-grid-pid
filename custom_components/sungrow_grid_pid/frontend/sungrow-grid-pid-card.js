const CARD_VERSION="4.0.6";
class SungrowGridPidCard extends HTMLElement {
  constructor(){super();this.attachShadow({mode:"open"});this._config={};this._editing=null;}
  setConfig(v){this._config=v||{};this.render();}
  set hass(h){this._hass=h;if(!this._editing)this.render();}
  getCardSize(){return 7;}
  static getStubConfig(){return {};}
  _value(id){const v=this._hass?.states[id]?.state;return v===undefined?"—":v;}
  _fmt(id){const v=Number(this._value(id));return Number.isFinite(v)?v.toLocaleString():"—";}
  _send(domain,service,data){return this._hass.callService(domain,service,data);}
  _more(id){this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:id},bubbles:true,composed:true}));}
  render(){
    if(!this._hass)return;
    const settings=[
      ["Export Target SP","number.sem_export_target","W","Желаемая мощность экспорта в сеть. Например, 14 000 Вт."],
      ["Export Dead Band","number.sem_dead_band","W","Допустимое отклонение от Export Target в обе стороны. Пока экспорт в этом диапазоне, зарядка не изменяется."],
      ["Export Delay Time","number.sem_delay","s","Сколько секунд отклонение должно непрерывно оставаться за пределами Dead Band до одного шага регулировки."],
      ["Charge Gain SP","number.sem_charge_gain","W","На сколько ватт увеличивать или уменьшать лимит зарядки после истечения таймера."],
      ["Empty SOC SP","number.sem_empty_soc","%","Утром принудительная разрядка запускается, только если фактический SOC выше этого порога и резерва батареи."],
      ["Battery Forced Discharge Power","number.sem_discharge_power","W","Лимит мощности принудительной разрядки. Изменения во время активной разрядки сразу отправляются инвертору."]
    ];
    const gridOn=this._value("switch.sem_grid_target")==="on";
    const morningOn=this._value("switch.sem_morning_discharge")==="on";
    const charging=this._config.charge_entity||"number.battery_max_charge_power";
    const exportId=this._config.export_entity||"sensor.export_power";
    const input=(label,id,unit,description)=>{
      const obj=this._hass.states[id];
      return `<label class="setting"><span class="settingText"><strong>${label}</strong><small class="help">${description}</small></span><div class="edit"><input data-entity="${id}" type="number" inputmode="decimal" min="${obj?.attributes.min??0}" max="${obj?.attributes.max??100000}" step="${obj?.attributes.step??1}" value="${obj && Number.isFinite(Number(obj.state)) ? Math.round(Number(obj.state)) : (obj?.state??'')}" ${obj?"":"disabled"} /><small>${unit}</small></div></label>`;
    };
    this.shadowRoot.innerHTML=`<style>\n      .settingText{display:flex;flex-direction:column;gap:3px;flex:1;min-width:0}.settingText strong{font-weight:500}.settingText .help{display:block;line-height:1.35;color:var(--secondary-text-color);font-size:11px;max-width:330px}
      *{box-sizing:border-box}ha-card{padding:16px;border-radius:16px;color:var(--primary-text-color)}
      .title{font-size:20px;font-weight:700}.muted{font-size:12px;color:var(--secondary-text-color)}
      .header,.line,.setting,.edit,.stats{display:flex;align-items:center;justify-content:space-between;gap:12px}
      .section{border-top:1px solid var(--divider-color);padding-top:14px;margin-top:14px}
      .setting{margin:10px 0;font-size:13px}.edit{gap:6px}input{width:112px;min-width:0;padding:9px 8px;border:1px solid var(--divider-color);border-radius:9px;background:var(--card-background-color);color:var(--primary-text-color);font:inherit;font-size:14px}
      input[type=time]{width:120px}small{min-width:18px;color:var(--secondary-text-color)}
      button{background:var(--secondary-background-color);border:1px solid var(--divider-color);color:var(--primary-text-color);border-radius:9px;padding:9px 12px;cursor:pointer}
      button.on{background:var(--success-color,#388e3c);color:white}
      button:disabled{opacity:.5}.stats{margin-top:14px}.stat{flex:1;background:var(--secondary-background-color);padding:12px;border-radius:10px;cursor:pointer}.stat b{display:block;font-size:19px;margin-top:5px}
      .status{margin-top:10px;padding:10px;background:var(--secondary-background-color);border-radius:9px;font-size:12px}
      @media(max-width:430px){.setting{align-items:flex-start}.setting span{max-width:54%}input{width:96px}.settingText .help{font-size:10px}.stats{gap:7px}.stat{padding:9px}.stat b{font-size:16px}}
    </style><ha-card>
      <div class="header"><div><div class="title">Sungrow Energy Manager</div><div class="muted">SEM v${CARD_VERSION} · Grid & Battery Control</div></div><button data-switch="switch.sem_grid_target" class="${gridOn?"on":""}">${gridOn?"STOP":"START"}</button></div>
      <div class="stats"><div class="stat" data-more="${exportId}"><span class="muted">Grid Export</span><b>${this._fmt(exportId)} W</b></div><div class="stat" data-more="sensor.sungrow_pid_charge_history"><span class="muted">Battery Charge SP</span><b>${this._fmt(charging)} W</b></div></div>
      <div class="section"><div class="line"><strong>Grid Target</strong><span class="muted">${gridOn?"Active":"Stopped"}</span></div>
      ${settings.slice(0,4).map(i=>input(...i)).join("")}
      <div class="status">${this._value("sensor.sem_manager_status")}</div></div>
      <div class="section"><div class="line"><strong>Battery Morning Discharge</strong><button data-switch="switch.sem_morning_discharge" class="${morningOn?"on":""}">${morningOn?"ON":"OFF"}</button></div>
      <label class="setting"><span>Start Time</span><div class="edit"><input type="time" data-time="time.sem_morning_start" value="${this._value("time.sem_morning_start").slice(0,5)}"></div></label>
      ${settings.slice(4).map(i=>input(...i)).join("")}
      <div class="muted">Stop SOC: Battery Reserved SoC for Backup (selected in integration options)</div><div class="status">Morning Discharge: ${this._value("sensor.sem_morning_discharge_status")}</div></div>
    </ha-card>`;
    this.shadowRoot.querySelectorAll("[data-switch]").forEach(btn=>btn.onclick=async()=>{
      btn.disabled=true;
      try{await this._send("switch",this._value(btn.dataset.switch)==="on"?"turn_off":"turn_on",{entity_id:btn.dataset.switch});}
      catch(e){console.error("SEM switch error",e);alert("SEM: "+e.message);}finally{btn.disabled=false;}
    });
    this.shadowRoot.querySelectorAll("[data-entity]").forEach(el=>{
      el.onfocus=()=>{this._editing=el.dataset.entity;};
      el.onblur=()=>{this._editing=null;};
      el.onchange=async()=>{
        try{await this._send("number","set_value",{entity_id:el.dataset.entity,value:Number(el.value)});}
        catch(e){console.error("SEM set value error",e);alert("SEM: "+e.message);}
        finally{this._editing=null;this.render();}
      };
    });
    this.shadowRoot.querySelectorAll("[data-time]").forEach(el=>{
      el.onfocus=()=>{this._editing="time";};
      el.onblur=()=>{this._editing=null;};
      el.onchange=async()=>{try{await this._send("time","set_value",{entity_id:el.dataset.time,time:el.value+":00"});}
      catch(e){console.error(e);alert("SEM: "+e.message);}finally{this._editing=null;this.render();}};
    });
    this.shadowRoot.querySelectorAll("[data-more]").forEach(el=>el.onclick=()=>this._more(this._hass.states[el.dataset.more]?el.dataset.more:charging));
  }
}
if(customElements.get("sungrow-grid-pid-card")){
 const proto=customElements.get("sungrow-grid-pid-card").prototype;
 for(const key of Object.getOwnPropertyNames(SungrowGridPidCard.prototype)){if(key!=="constructor")Object.defineProperty(proto,key,Object.getOwnPropertyDescriptor(SungrowGridPidCard.prototype,key));}
}else customElements.define("sungrow-grid-pid-card",SungrowGridPidCard);
window.customCards=window.customCards||[];
if(!window.customCards.some(c=>c.type==="sungrow-grid-pid-card"))window.customCards.push({type:"sungrow-grid-pid-card",name:"Sungrow Energy Manager",description:"Stepped export control and scheduled morning battery discharge",preview:false});
