const CARD_VERSION="4.0.7";
class SungrowGridPidCard extends HTMLElement {
  constructor(){super();this.attachShadow({mode:"open"});this._config={};this._editing=null;this._timePickerEngaged=false;this._pendingTimeValue=null;}
  setConfig(v){
    const next=v||{};
    const changed=JSON.stringify(next)!==JSON.stringify(this._config);
    this._config=next;
    if(changed || !this.shadowRoot.querySelector("ha-card"))this.render();
    else this.updateLive();
  }
  set hass(h){
    this._hass=h;
    // Never replace the time input when HA publishes new states.
    // Replacing it closes the browser's native time picker on desktop/mobile.
    if(!this.shadowRoot.querySelector("ha-card"))this.render();
    else this.updateLive();
  }
  getCardSize(){return 7;}
  static getStubConfig(){return {};}
  _value(id){const v=this._hass?.states[id]?.state;return v===undefined?"—":v;}
  _fmt(id){const v=Number(this._value(id));return Number.isFinite(v)?v.toLocaleString():"—";}
  _send(domain,service,data){return this._hass.callService(domain,service,data);}
  _more(id){this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:id},bubbles:true,composed:true}));}
  updateLive(){
    if(!this._hass)return;
    const root=this.shadowRoot;
    const exportId=this._config.export_entity||"sensor.export_power";
    const chargeId=this._config.charge_entity||"number.battery_max_charge_power";
    const setText=(selector,text)=>{
      const node=root.querySelector(selector);
      if(node && node.textContent!==text)node.textContent=text;
    };
    setText('[data-stat="export"] b',this._fmt(exportId)+" W");
    setText('[data-stat="charge"] b',this._fmt(chargeId)+" W");
    const gridOn=this._value("switch.sem_grid_target")==="on";
    const morningOn=this._value("switch.sem_morning_discharge")==="on";
    setText("[data-grid-state]",gridOn?"Active":"Stopped");
    setText("[data-grid-status]",this._value("sensor.sem_manager_status"));
    setText("[data-morning-status]","Morning Discharge: "+this._value("sensor.sem_morning_discharge_status"));
    for(const [entityId,isOn,onText,offText] of [
      ["switch.sem_grid_target",gridOn,"STOP","START"],
      ["switch.sem_morning_discharge",morningOn,"ON","OFF"]
    ]){
      const btn=root.querySelector('[data-switch="'+entityId+'"]');
      if(btn){
        btn.classList.toggle("on",isOn);
        if(btn.textContent!==(isOn?onText:offText))btn.textContent=isOn?onText:offText;
      }
    }
    // Refresh non-edited SP values without destroying or replacing any controls.
    root.querySelectorAll("[data-entity]").forEach(el=>{
      if(el===root.activeElement || this._editing===el.dataset.entity)return;
      const state=this._hass.states[el.dataset.entity];
      if(!state)return;
      const num=Number(state.state);
      const value=Number.isFinite(num)?String(Math.round(num)):state.state;
      if(el.value!==value)el.value=value;
    });
    const timeInput=root.querySelector("[data-time]");
    if(timeInput){
      const time=this._value(timeInput.dataset.time).slice(0,5);
      // Avoid reverting a just-saved value while HA is still publishing it.
      if(this._pendingTimeValue===time)this._pendingTimeValue=null;
      if(!this._timePickerEngaged && !this._pendingTimeValue && timeInput!==root.activeElement
         && /^\d{2}:\d{2}$/.test(time) && timeInput.value!==time)timeInput.value=time;
    }
  }
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
      <div class="stats"><div class="stat" data-stat="export" data-more="${exportId}"><span class="muted">Grid Export</span><b>${this._fmt(exportId)} W</b></div><div class="stat" data-stat="charge" data-more="sensor.sungrow_pid_charge_history"><span class="muted">Battery Charge SP</span><b>${this._fmt(charging)} W</b></div></div>
      <div class="section"><div class="line"><strong>Grid Target</strong><span class="muted" data-grid-state>${gridOn?"Active":"Stopped"}</span></div>
      ${settings.slice(0,4).map(i=>input(...i)).join("")}
      <div class="status" data-grid-status>${this._value("sensor.sem_manager_status")}</div></div>
      <div class="section"><div class="line"><strong>Battery Morning Discharge</strong><button data-switch="switch.sem_morning_discharge" class="${morningOn?"on":""}">${morningOn?"ON":"OFF"}</button></div>
      <label class="setting"><span>Start Time</span><div class="edit"><input type="time" data-time="time.sem_morning_start" value="${this._value("time.sem_morning_start").slice(0,5)}"></div></label>
      ${settings.slice(4).map(i=>input(...i)).join("")}
      <div class="muted">Stop SOC: Battery Reserved SoC for Backup (selected in integration options)</div><div class="status" data-morning-status>Morning Discharge: ${this._value("sensor.sem_morning_discharge_status")}</div></div>
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
        finally{this._editing=null;this.updateLive();}
      };
    });
    this.shadowRoot.querySelectorAll("[data-time]").forEach(el=>{
      // The native time picker can temporarily blur the input while its popup
      // is still open. Keep the node and its draft value intact in that case.
      el.onpointerdown=()=>{this._timePickerEngaged=true;};
      el.onfocus=()=>{this._timePickerEngaged=true;this._editing="time";};
      el.onblur=()=>{this._editing=null;};
      el.onchange=async()=>{
        this._timePickerEngaged=true;
        const newTime=el.value;
        try{
          if(/^\d{2}:\d{2}$/.test(newTime)){
            this._pendingTimeValue=newTime;
            await this._send("time","set_value",{entity_id:el.dataset.time,time:newTime+":00"});
          }
        }catch(e){
          this._pendingTimeValue=null;
          console.error("SEM time update error",e);
          alert("SEM: "+e.message);
        }
        finally{this._editing=null;this._timePickerEngaged=false;this.updateLive();}
      };
    });
    // Clicking elsewhere inside the card releases a dismissed native picker,
    // without requiring the browser to fire a blur/change event.
    this.shadowRoot.addEventListener("pointerdown",e=>{
      if(e.target!==this.shadowRoot.querySelector("[data-time]")){
        this._timePickerEngaged=false;
      }
    });
    this.updateLive();
    this.shadowRoot.querySelectorAll("[data-more]").forEach(el=>el.onclick=()=>this._more(this._hass.states[el.dataset.more]?el.dataset.more:charging));
  }
}
if(customElements.get("sungrow-grid-pid-card")){
 const proto=customElements.get("sungrow-grid-pid-card").prototype;
 for(const key of Object.getOwnPropertyNames(SungrowGridPidCard.prototype)){if(key!=="constructor")Object.defineProperty(proto,key,Object.getOwnPropertyDescriptor(SungrowGridPidCard.prototype,key));}
}else customElements.define("sungrow-grid-pid-card",SungrowGridPidCard);
window.customCards=window.customCards||[];
if(!window.customCards.some(c=>c.type==="sungrow-grid-pid-card"))window.customCards.push({type:"sungrow-grid-pid-card",name:"Sungrow Energy Manager",description:"Stepped export control and scheduled morning battery discharge",preview:false});
