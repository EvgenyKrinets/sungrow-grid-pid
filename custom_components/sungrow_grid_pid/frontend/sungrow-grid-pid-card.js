const CARD_VERSION = "1.4.0";

class SungrowGridPidCard extends HTMLElement {
  constructor() { super(); this.attachShadow({mode:"open"}); this._config={}; this._hass=null; }
  static getStubConfig(){ return {}; }
  setConfig(c){ this._config=c||{}; this._render(); }
  set hass(h){ this._hass=h; this._render(); }
  getCardSize(){ return 9; }

  _find(domain, preferred, names=[], contains=[]){
    if(!this._hass) return null;
    if(preferred && this._hass.states[preferred]) return preferred;
    const a=Object.entries(this._hass.states).filter(([id])=>id.startsWith(domain+"."));
    for(const [id,s] of a){const f=String(s.attributes.friendly_name||"").toLowerCase(); if(names.some(n=>f===n.toLowerCase())) return id;}
    for(const [id,s] of a){const h=(id+" "+String(s.attributes.friendly_name||"")).toLowerCase(); if(contains.every(x=>h.includes(x))) return id;}
    return null;
  }
  _entities(){
    return {
      controller:this._find("switch",this._config.controller_entity,["PID Grid Controller"],["pid","grid","controller"]),
      target:this._find("number",this._config.target_entity,["PID Grid Target"],["pid","grid","target"]),
      output:this._find("sensor",this._config.output_entity,["PID Output"],["pid","output"]),
      error:this._find("sensor",this._config.error_entity,["PID Grid Error"],["pid","grid","error"]),
      version:this._find("sensor",this._config.version_entity,["Sungrow Grid PID Version"],["grid","pid","version"]),
      exportPower:this._find("sensor",this._config.export_entity||"sensor.export_power",["Export Power"],["export","power"]),
      chargeCommand:this._find("number",this._config.charge_entity||"number.battery_max_charge_power",["Battery Max Charge Power"],["charge","power"]),
      pv:this._find("sensor",this._config.pv_entity,["Total PV Power","PV Power"],["pv","power"]),
      load:this._find("sensor",this._config.load_entity,["Load Power","House Load"],["load","power"]),
      battery:this._find("sensor",this._config.battery_power_entity,["Battery Power"],["battery","power"]),
      soc:this._find("sensor",this._config.soc_entity,["Battery Level","Battery SOC"],["battery","level"])
          ||this._find("sensor",this._config.soc_entity,["Battery SOC"],["battery","soc"]),
      inverter:this._find("sensor",this._config.inverter_entity,["Inverter Power"],["inverter","power"])
    };
  }
  _state(id,f="—"){return id&&this._hass?.states[id]?this._hass.states[id].state:f;}
  _n(id){const v=Number(this._state(id,NaN));return Number.isFinite(v)?v:null;}
  _power(id){const v=this._n(id); if(v===null)return "—"; return Math.abs(v)>=1000?(v/1000).toFixed(2)+" kW":Math.round(v)+" W";}
  _call(d,s,data){if(this._hass)this._hass.callService(d,s,data);}
  _render(){
    if(!this.shadowRoot)return;
    const e=this._entities(), enabled=this._state(e.controller)==="on";
    const ts=e.target&&this._hass?.states[e.target], target=Number(ts?.state||15000);
    const min=Number(ts?.attributes.min??0), max=Number(ts?.attributes.max??25000), step=Number(ts?.attributes.step??1000);
    const batt=this._n(e.battery), exp=this._n(e.exportPower);
    const batteryLabel=batt===null?"Battery":batt>20?"Battery · charging":batt<-20?"Battery · discharging":"Battery · idle";
    const gridLabel=exp===null?"Grid":exp>=0?"Grid · export":"Grid · import";
    this.shadowRoot.innerHTML=`
<style>
:host{display:block}*{box-sizing:border-box}ha-card{overflow:hidden;border-radius:24px;background:linear-gradient(145deg,#0878d1,#159ee4 58%,#39b7ef);color:#fff;padding:18px;box-shadow:0 10px 28px #0002}
.head{display:flex;justify-content:space-between;align-items:center;gap:12px}.title{font-size:23px;font-weight:800}.sub{opacity:.82;font-size:12px;margin-top:3px}
.toggle{border:0;width:52px;height:30px;padding:3px;border-radius:20px;background:#ffffff55}.toggle.on{background:#45e78c}.knob{display:block;width:24px;height:24px;border-radius:50%;background:#fff;box-shadow:0 2px 5px #0005;transition:.2s}.toggle.on .knob{transform:translateX(22px)}
.flow{position:relative;display:grid;grid-template-columns:1fr 1fr 1fr;grid-template-areas:"solar inv home" ". battery grid";gap:12px;margin-top:18px}.node{position:relative;z-index:2;background:#fff;color:#17243b;border-radius:18px;padding:13px;text-align:center;min-height:112px;box-shadow:0 6px 18px #005b9b33}.solar{grid-area:solar}.inv{grid-area:inv}.home{grid-area:home}.battery{grid-area:battery}.gridnode{grid-area:grid}.ico{font-size:30px;line-height:34px}.name{font-size:12px;color:#68768a;margin-top:3px}.val{font-size:20px;font-weight:800;margin-top:5px}.small{font-size:10px;color:#159447;margin-top:4px}
.arrow{position:absolute;height:5px;border-radius:6px;background:#8affb8;z-index:1;box-shadow:0 0 10px #5bff93;animation:pulse 1.2s infinite alternate}.a1{left:28%;top:55px;width:12%}.a2{left:61%;top:55px;width:10%}.a3{left:47%;top:155px;width:16%;transform:rotate(28deg)}.a4{right:14%;top:155px;width:16%;transform:rotate(90deg)}@keyframes pulse{from{opacity:.45}to{opacity:1}}
.control{margin-top:16px;background:#ffffffee;color:#17243b;border-radius:18px;padding:15px}.targetline{display:flex;justify-content:space-between;align-items:baseline}.targetline b{font-size:22px}input[type=range]{width:100%;accent-color:#078ad4;margin:12px 0 3px}.limits{display:flex;justify-content:space-between;font-size:10px;color:#718096}
.metrics{display:grid;grid-template-columns:repeat(2,1fr);gap:9px;margin-top:12px}.metric{background:#ffffff22;border:1px solid #ffffff25;border-radius:14px;padding:11px}.ml{font-size:11px;opacity:.8}.mv{font-size:17px;font-weight:750;margin-top:4px}.footer{display:flex;justify-content:space-between;font-size:11px;opacity:.82;margin-top:13px}.missing{background:#ffdfdf;color:#9b1c1c;border-radius:12px;padding:10px;margin-top:12px;font-size:11px}
@media(max-width:520px){ha-card{padding:13px;border-radius:20px}.flow{grid-template-columns:1fr 1fr;grid-template-areas:"solar inv" "home grid" "battery battery"}.arrow{display:none}.node{min-height:98px}.val{font-size:18px}.metrics{grid-template-columns:1fr 1fr}}
</style>
<ha-card>
<div class="head"><div><div class="title">⚡ Sungrow Grid PID</div><div class="sub">Live solar energy flow · 1-second grid controller</div></div><button id="toggle" class="toggle ${enabled?"on":""}"><span class="knob"></span></button></div>
<div class="flow">
<div class="arrow a1"></div><div class="arrow a2"></div><div class="arrow a3"></div><div class="arrow a4"></div>
<div class="node solar"><div class="ico">☀️</div><div class="name">Solar PV</div><div class="val">${this._power(e.pv)}</div><div class="small">solar production</div></div>
<div class="node inv"><div class="ico">⚡</div><div class="name">Sungrow inverter</div><div class="val">${this._power(e.inverter)}</div><div class="small">power conversion</div></div>
<div class="node home"><div class="ico">🏠</div><div class="name">Home load</div><div class="val">${this._power(e.load)}</div><div class="small">house consumption</div></div>
<div class="node battery"><div class="ico">🔋</div><div class="name">${batteryLabel}</div><div class="val">${this._power(e.battery)}</div><div class="small">SOC ${e.soc?this._state(e.soc)+"%":"—"}</div></div>
<div class="node gridnode"><div class="ico">🔌</div><div class="name">${gridLabel}</div><div class="val">${this._power(e.exportPower)}</div><div class="small">target ${Math.round(target).toLocaleString()} W</div></div>
</div>
<div class="control"><div class="targetline"><span>Grid Target</span><b>${Math.round(target).toLocaleString()} W</b></div><input id="target" type="range" min="${min}" max="${max}" step="${step}" value="${target}" ${e.target?"":"disabled"}><div class="limits"><span>${min.toLocaleString()} W</span><span>${max.toLocaleString()} W</span></div></div>
<div class="metrics">
<div class="metric"><div class="ml">PID Output</div><div class="mv">${this._power(e.output)}</div></div>
<div class="metric"><div class="ml">Grid Error</div><div class="mv">${this._power(e.error)}</div></div>
<div class="metric"><div class="ml">Battery Charge Command</div><div class="mv">${this._power(e.chargeCommand)}</div></div>
<div class="metric"><div class="ml">Controller</div><div class="mv">${enabled?"● Running":"○ Stopped"}</div></div>
</div>
<div class="footer"><span>Updates from Home Assistant live states</span><span>v${this._state(e.version,CARD_VERSION)}</span></div>
${(!e.controller||!e.target)?'<div class="missing">PID entities not found. Add Sungrow Grid PID in Settings → Devices & services.</div>':""}
</ha-card>`;
    this.shadowRoot.getElementById("toggle")?.addEventListener("click",()=>{if(e.controller)this._call("switch",enabled?"turn_off":"turn_on",{entity_id:e.controller});});
    const sl=this.shadowRoot.getElementById("target");
    sl?.addEventListener("input",ev=>{const b=this.shadowRoot.querySelector(".targetline b");if(b)b.textContent=Math.round(Number(ev.target.value)).toLocaleString()+" W";});
    sl?.addEventListener("change",ev=>{if(e.target)this._call("number","set_value",{entity_id:e.target,value:Number(ev.target.value)});});
  }
}
function registerSungrowGridPidCard(){
 if(!customElements.get("sungrow-grid-pid-card"))customElements.define("sungrow-grid-pid-card",SungrowGridPidCard);
 window.customCards=window.customCards||[];
 if(!window.customCards.some(c=>c.type==="sungrow-grid-pid-card"))window.customCards.push({type:"sungrow-grid-pid-card",name:"Sungrow Grid PID",description:"Visual Sungrow solar flow and PID grid export controller.",preview:true,documentationURL:"https://github.com/EvgenyKrinets/sungrow-grid-pid"});
}
registerSungrowGridPidCard(); window.addEventListener("load",()=>setTimeout(registerSungrowGridPidCard,1000),{once:true}); setTimeout(registerSungrowGridPidCard,2500);
