const CARD_VERSION="4.0.10";
const SEM_TRANSLATIONS={"en":{"Grid & Battery Control":"Grid & Battery Control","Active":"Active","Stopped":"Stopped","Grid Export":"Grid Export","Battery Charge SP":"Battery Charge SP","Grid Target":"Grid Target","Battery Morning Discharge":"Battery Morning Discharge","Start Time":"Start Time","Stop SOC: Battery Reserved SoC for Backup (selected in integration options)":"Stop SOC: Battery Reserved SoC for Backup (selected in integration options)","Morning Discharge":"Morning Discharge","Night Tariff Mode":"Night Tariff Mode","Discount Start":"Discount Start","Discount End":"Discount End","Night Tariff":"Night Tariff","Discounted starting nights":"Discounted starting nights","During discount: Self-Consumption (no battery discharge). Outside: Self-Consumption (max battery discharge).":"During discount: Self-Consumption (no battery discharge). Outside: Self-Consumption (max battery discharge).","Configure the no-battery-discharge scene in the integration options. Verify the scene really blocks battery discharge.":"Configure the no-battery-discharge scene in integration options. Verify that it blocks battery discharge.","Monday":"Mon","Tuesday":"Tue","Wednesday":"Wed","Thursday":"Thu","Friday":"Fri","Saturday":"Sat","Sunday":"Sun","Export Target SP":"Export Target SP","Export Dead Band":"Export Dead Band","Export Delay Time":"Export Delay Time","Charge Gain SP":"Charge Gain SP","Empty SOC SP":"Empty SOC SP","Battery Forced Discharge Power":"Battery Forced Discharge Power","Желаемая мощность экспорта в сеть. Например, 14 000 Вт.":"Desired grid export power, for example 14,000 W.","Допустимое отклонение от Export Target в обе стороны. Пока экспорт в этом диапазоне, зарядка не изменяется.":"Allowed deviation from export target in either direction. No change while inside the band.","Сколько секунд отклонение должно непрерывно оставаться за пределами Dead Band до одного шага регулировки.":"Seconds the deviation must persist outside the dead band before a control step.","На сколько ватт увеличивать или уменьшать лимит зарядки после истечения таймера.":"Amount in watts to adjust the charge limit after the delay.","Утром принудительная разрядка запускается, только если фактический SOC выше этого порога и резерва батареи.":"Morning forced discharge starts only above this SOC and the backup reserve.","Лимит мощности принудительной разрядки. Изменения во время активной разрядки сразу отправляются инвертору.":"Forced discharge power limit. Changes during discharge are sent immediately."},"ru":{"Grid & Battery Control":"Управление сетью и батареей","Active":"Работает","Stopped":"Остановлено","Grid Export":"Экспорт в сеть","Battery Charge SP":"Лимит зарядки батареи","Grid Target":"Контроль экспорта","Battery Morning Discharge":"Утренняя разрядка","Start Time":"Время начала","Stop SOC: Battery Reserved SoC for Backup (selected in integration options)":"Остановка по резерву SOC, выбранному в настройках интеграции","Morning Discharge":"Утренняя разрядка","Night Tariff Mode":"Ночной тариф","Discount Start":"Начало скидки","Discount End":"Конец скидки","Night Tariff":"Ночной тариф","Discounted starting nights":"Дни начала скидки","During discount: Self-Consumption (no battery discharge). Outside: Self-Consumption (max battery discharge).":"Во время скидки разрядка запрещена; вне скидки обычная самообеспечивающая сцена.","Configure the no-battery-discharge scene in the integration options. Verify the scene really blocks battery discharge.":"Выберите сцену без разрядки в настройках интеграции и проверьте её работу.","Monday":"Пн","Tuesday":"Вт","Wednesday":"Ср","Thursday":"Чт","Friday":"Пт","Saturday":"Сб","Sunday":"Вс","Export Target SP":"Цель экспорта","Export Dead Band":"Допустимое отклонение","Export Delay Time":"Задержка регулировки","Charge Gain SP":"Шаг зарядки","Empty SOC SP":"Порог SOC утром","Battery Forced Discharge Power":"Мощность принудительной разрядки"},"he":{"Grid & Battery Control":"בקרת רשת וסוללה","Active":"פעיל","Stopped":"מופסק","Grid Export":"ייצוא לרשת","Battery Charge SP":"מגבלת טעינת סוללה","Grid Target":"יעד ייצוא לרשת","Battery Morning Discharge":"פריקת סוללה בבוקר","Start Time":"שעת התחלה","Stop SOC: Battery Reserved SoC for Backup (selected in integration options)":"עצירה לפי רזרבת SOC שנבחרה בהגדרות","Morning Discharge":"פריקת בוקר","Night Tariff Mode":"תעריף לילה","Discount Start":"תחילת ההנחה","Discount End":"סיום ההנחה","Night Tariff":"תעריף לילה","Discounted starting nights":"ימי תחילת ההנחה","During discount: Self-Consumption (no battery discharge). Outside: Self-Consumption (max battery discharge).":"בשעות ההנחה אין פריקת סוללה; מחוץ להן פועלת סצנת הצריכה העצמית הרגילה.","Configure the no-battery-discharge scene in the integration options. Verify the scene really blocks battery discharge.":"בחר סצנה ללא פריקה בהגדרות האינטגרציה וודא שהיא אכן מונעת פריקה.","Monday":"ב׳","Tuesday":"ג׳","Wednesday":"ד׳","Thursday":"ה׳","Friday":"ו׳","Saturday":"ש׳","Sunday":"א׳","Export Target SP":"יעד הספק הייצוא","Export Dead Band":"תחום סטייה מותר","Export Delay Time":"השהיית ויסות","Charge Gain SP":"צעד הספק טעינה","Empty SOC SP":"סף SOC בבוקר","Battery Forced Discharge Power":"הספק פריקה מאולצת","Желаемая мощность экспорта в сеть. Например, 14 000 Вт.":"הספק הייצוא הרצוי לרשת, לדוגמה 14,000 ואט.","Допустимое отклонение от Export Target в обе стороны. Пока экспорт в этом диапазоне, зарядка не изменяется.":"סטייה מותרת מיעד הייצוא לשני הכיוונים. בגבולות התחום הטעינה לא משתנה.","Сколько секунд отклонение должно непрерывно оставаться за пределами Dead Band до одного шага регулировки.":"משך הסטייה הרצופה מחוץ לתחום המותר לפני צעד ויסות.","На сколько ватт увеличивать или уменьшать лимит зарядки после истечения таймера.":"גודל שינוי מגבלת הטעינה בוואט לאחר ההשהיה.","Утром принудительная разрядка запускается, только если фактический SOC выше этого порога и резерва батареи.":"פריקת הבוקר תתחיל רק אם SOC גבוה מהסף הזה ומרזרבת הגיבוי.","Лимит мощности принудительной разрядки. Изменения во время активной разрядки сразу отправляются инвертору.":"מגבלת הספק פריקה מאולצת. שינויים במהלך פריקה נשלחים מיד לממיר."}};
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
    const languageChanged=Boolean(this._hass && this._hass.language!==h.language);
    this._hass=h;
    if(languageChanged){this.render();return;}
    // Never replace the time input when HA publishes new states.
    // Replacing it closes the browser's native time picker on desktop/mobile.
    if(!this.shadowRoot.querySelector("ha-card"))this.render();
    else this.updateLive();
  }
  _tr(key){const lang=(this._hass?.language||"en").split("-")[0];return SEM_TRANSLATIONS[lang]?.[key]||SEM_TRANSLATIONS.en[key]||key;}
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
    const tariffOn=this._value("switch.sem_night_tariff")==="on";
    setText("[data-grid-state]",this._tr(gridOn?"Active":"Stopped"));
    setText("[data-grid-status]",this._value("sensor.sem_manager_status"));
    setText("[data-morning-status]",this._tr("Morning Discharge")+": "+this._value("sensor.sem_morning_discharge_status"));
    setText("[data-tariff-status]",this._tr("Night Tariff")+": "+this._value("sensor.sem_night_tariff_status"));
    for(const [entityId,isOn,onText,offText] of [
      ["switch.sem_grid_target",gridOn,"STOP","START"],
      ["switch.sem_morning_discharge",morningOn,"ON","OFF"],
      ["switch.sem_night_tariff",tariffOn,"ON","OFF"]
    ]){
      const btn=root.querySelector('[data-switch="'+entityId+'"]');
      if(btn){
        btn.classList.toggle("on",isOn);
        if(btn.textContent!==(isOn?onText:offText))btn.textContent=isOn?onText:offText;
      }
    }
    root.querySelectorAll("[data-day]").forEach(btn=>{btn.classList.toggle("on",this._value(btn.dataset.day)==="on");});
    // Refresh non-edited SP values without destroying or replacing any controls.
    root.querySelectorAll("[data-entity]").forEach(el=>{
      if(el===root.activeElement || this._editing===el.dataset.entity)return;
      const state=this._hass.states[el.dataset.entity];
      if(!state)return;
      const num=Number(state.state);
      const value=Number.isFinite(num)?String(Math.round(num)):state.state;
      if(el.value!==value)el.value=value;
    });
    root.querySelectorAll("[data-time]").forEach(timeInput=>{
      const time=this._value(timeInput.dataset.time).slice(0,5);
      const pending=this._pendingTimeValue;
      if(pending && pending.entityId===timeInput.dataset.time && pending.value===time)
        this._pendingTimeValue=null;
      const waitForThis=pending && pending.entityId===timeInput.dataset.time;
      if(!this._timePickerEngaged && !waitForThis && timeInput!==root.activeElement
         && /^\d{2}:\d{2}$/.test(time) && timeInput.value!==time)timeInput.value=time;
    });
  }
  render(){
    if(!this._hass)return;
    const days=[this._tr("Sunday"),"Monday","Tuesday","Wednesday","Thursday","Friday",this._tr("Saturday")];
    const settings=[
      [this._tr("Export Target SP"),"number.sem_export_target","W",this._tr("Желаемая мощность экспорта в сеть. Например, 14 000 Вт.")],
      [this._tr("Export Dead Band"),"number.sem_dead_band","W",this._tr("Допустимое отклонение от Export Target в обе стороны. Пока экспорт в этом диапазоне, зарядка не изменяется.")],
      [this._tr("Export Delay Time"),"number.sem_delay","s",this._tr("Сколько секунд отклонение должно непрерывно оставаться за пределами Dead Band до одного шага регулировки.")],
      [this._tr("Charge Gain SP"),"number.sem_charge_gain","W",this._tr("На сколько ватт увеличивать или уменьшать лимит зарядки после истечения таймера.")],
      [this._tr("Empty SOC SP"),"number.sem_empty_soc","%",this._tr("Утром принудительная разрядка запускается, только если фактический SOC выше этого порога и резерва батареи.")],
      [this._tr("Battery Forced Discharge Power"),"number.sem_discharge_power","W",this._tr("Лимит мощности принудительной разрядки. Изменения во время активной разрядки сразу отправляются инвертору.")]
    ];
    const gridOn=this._value("switch.sem_grid_target")==="on";
    const morningOn=this._value("switch.sem_morning_discharge")==="on";
    const tariffOn=this._value("switch.sem_night_tariff")==="on";
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
      <div class="header"><div><div class="title">Sungrow Energy Manager</div><div class="muted">SEM v${CARD_VERSION} · ${this._tr("Grid & Battery Control")}</div></div><button data-switch="switch.sem_grid_target" class="${gridOn?"on":""}">${gridOn?"STOP":"START"}</button></div>
      <div class="stats"><div class="stat" data-stat="export" data-more="${exportId}"><span class="muted">${this._tr("Grid Export")}</span><b>${this._fmt(exportId)} W</b></div><div class="stat" data-stat="charge" data-more="sensor.sungrow_pid_charge_history"><span class="muted">${this._tr("Battery Charge SP")}</span><b>${this._fmt(charging)} W</b></div></div>
      <div class="section"><div class="line"><strong>${this._tr("Grid Target")}</strong><span class="muted" data-grid-state>${gridOn?"Active":"Stopped"}</span></div>
      ${settings.slice(0,4).map(i=>input(...i)).join("")}
      <div class="status" data-grid-status>${this._value("sensor.sem_manager_status")}</div></div>
      <div class="section"><div class="line"><strong>${this._tr("Battery Morning Discharge")}</strong><button data-switch="switch.sem_morning_discharge" class="${morningOn?"on":""}">${morningOn?"ON":"OFF"}</button></div>
      <label class="setting"><span>${this._tr("Start Time")}</span><div class="edit"><input type="time" data-time="time.sem_morning_start" value="${this._value("time.sem_morning_start").slice(0,5)}"></div></label>
      ${settings.slice(4).map(i=>input(...i)).join("")}
      <div class="muted">${this._tr("Stop SOC: Battery Reserved SoC for Backup (selected in integration options)")}</div><div class="status" data-morning-status>Morning Discharge: ${this._value("sensor.sem_morning_discharge_status")}</div></div>
      <div class="section"><div class="line"><strong>${this._tr("Night Tariff Mode")}</strong><button data-switch="switch.sem_night_tariff" class="${tariffOn?"on":""}">${tariffOn?"ON":"OFF"}</button></div>
      <div class="muted" style="margin-top:8px">${this._tr("Discounted starting nights")} · Home Assistant</div>
      <div class="days" style="display:flex;gap:5px;flex-wrap:wrap;margin-top:8px">${days.map(day=>`<button data-day="switch.sem_discount_${day.toLowerCase()}" class="${this._value("switch.sem_discount_"+day.toLowerCase())==="on"?"on":""}">${this._tr(day)}</button>`).join("")}</div>
      <label class="setting"><span>${this._tr("Discount Start")}</span><div class="edit"><input type="time" data-time="time.sem_tariff_start" value="${this._value("time.sem_tariff_start").slice(0,5)}"></div></label>
      <label class="setting"><span>${this._tr("Discount End")}</span><div class="edit"><input type="time" data-time="time.sem_tariff_end" value="${this._value("time.sem_tariff_end").slice(0,5)}"></div></label>
      <div class="muted">${this._tr("During discount: Self-Consumption (no battery discharge). Outside: Self-Consumption (max battery discharge).")}</div>
      <div class="status" data-tariff-status>Night Tariff: ${this._value("sensor.sem_night_tariff_status")}</div>
      <div class="muted">${this._tr("Configure the no-battery-discharge scene in the integration options. Verify the scene really blocks battery discharge.")}</div></div>
    </ha-card>`;
    this.shadowRoot.querySelectorAll("[data-switch]").forEach(btn=>btn.onclick=async()=>{
      btn.disabled=true;
      try{await this._send("switch",this._value(btn.dataset.switch)==="on"?"turn_off":"turn_on",{entity_id:btn.dataset.switch});}
      catch(e){console.error("SEM switch error",e);alert("SEM: "+e.message);}finally{btn.disabled=false;}
    });
    this.shadowRoot.querySelectorAll("[data-day]").forEach(btn=>btn.onclick=async()=>{
      btn.disabled=true;
      try{await this._send("switch",this._value(btn.dataset.day)==="on"?"turn_off":"turn_on",{entity_id:btn.dataset.day});}
      catch(e){console.error("SEM discount day error",e);alert("SEM: "+e.message);}
      finally{btn.disabled=false;}
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
            this._pendingTimeValue={entityId:el.dataset.time,value:newTime};
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
    if(!this._pickerDismissListenerAdded){
      this.shadowRoot.addEventListener("pointerdown",e=>{
        if(!e.target || !e.target.matches || !e.target.matches("[data-time]")){
          this._timePickerEngaged=false;
        }
      });
      this._pickerDismissListenerAdded=true;
    }
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
