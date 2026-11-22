const CARD_VERSION="4.0.14";
const SEM_TRANSLATIONS={"en":{"Grid & Battery Control":"Grid & Battery Control","Active":"Active","Stopped":"Stopped","Grid Export":"Grid Export","Battery Charge SP":"Battery Charge SP","Grid Target":"Grid Target","Battery Morning Discharge":"Battery Morning Discharge","Start Time":"Start Time","Stop SOC: Battery Reserved SoC for Backup (selected in integration options)":"Stop SOC: Battery Reserved SoC for Backup (selected in integration options)","Morning Discharge":"Morning Discharge","Night Tariff Mode":"Night Tariff Mode","Discount Start":"Discount Start","Discount End":"Discount End","Night Tariff":"Night Tariff","Discounted starting nights":"Discounted starting nights","During discount: Self-Consumption (no battery discharge). Outside: Self-Consumption (max battery discharge).":"During discount: Self-Consumption (no battery discharge). Outside: Self-Consumption (max battery discharge).","No-discharge scene is detected automatically by its Home Assistant name. Verify the scene really blocks battery discharge.":"No-discharge scene is detected automatically by name. Verify that it prevents battery discharge.","Monday":"Mon","Tuesday":"Tue","Wednesday":"Wed","Thursday":"Thu","Friday":"Fri","Saturday":"Sat","Sunday":"Sun","Export Target SP":"Export Target SP","Export Dead Band":"Export Dead Band","Export Delay Time":"Export Delay Time","Charge Gain SP":"Charge Gain SP","Empty SOC SP":"Empty SOC SP","Battery Forced Discharge Power":"Battery Forced Discharge Power","Желаемая мощность экспорта в сеть. Например, 14 000 Вт.":"Desired grid export power, for example 14,000 W.","Допустимое отклонение от Export Target в обе стороны. Пока экспорт в этом диапазоне, зарядка не изменяется.":"Allowed deviation from export target in either direction. No change while inside the band.","Сколько секунд отклонение должно непрерывно оставаться за пределами Dead Band до одного шага регулировки.":"Seconds the deviation must persist outside the dead band before a control step.","На сколько ватт увеличивать или уменьшать лимит зарядки после истечения таймера.":"Amount in watts to adjust the charge limit after the delay.","Утром принудительная разрядка запускается, только если фактический SOC выше этого порога и резерва батареи.":"Morning forced discharge starts only above this SOC and the backup reserve.","Лимит мощности принудительной разрядки. Изменения во время активной разрядки сразу отправляются инвертору.":"Forced discharge power limit. Changes during discharge are sent immediately.","Off":"Off","Not run yet":"Not run yet","Grid Target: charge at minimum":"Grid Target: charge at minimum","Grid Target: charge at maximum":"Grid Target: charge at maximum","Grid Target: charge at limit":"Grid Target: charge at limit","Grid Target: within dead band":"Grid Target: within dead band","Grid Target active":"Grid Target active","Battery Forced Discharge":"Battery Forced Discharge","Waiting for Self-Consumption scene":"Waiting for Self-Consumption scene","Waiting for valid export / charging power":"Waiting for valid export / charging power","ERROR: charge adjustment failed":"ERROR: charge adjustment failed","ERROR: Self-Consumption scene failed":"ERROR: Self-Consumption scene failed","ERROR: recovery scene unavailable":"ERROR: recovery scene unavailable","ERROR: cannot exit forced discharge":"ERROR: cannot exit forced discharge","ERROR: SOC unavailable/invalid; reverting mode":"ERROR: SOC unavailable/invalid; reverting mode","Morning discharge command failed":"Morning discharge command failed","Cannot start: SOC or backup reserve unavailable":"Cannot start: SOC or backup reserve unavailable","Not configured: choose Forced Discharge scene and power number in integration options":"Not configured: choose Forced Discharge scene and power number in integration options","ERROR: service call failed; inspect HA logs":"ERROR: service call failed; inspect HA logs","ERROR: Forced Discharge power entity unavailable":"ERROR: Forced Discharge power entity unavailable","ERROR: unsafe SOC/reserve; discharge power not changed":"ERROR: unsafe SOC/reserve; discharge power not changed","ERROR: failed to update Forced Discharge power":"ERROR: failed to update Forced Discharge power","Recovery: ending forced discharge (state or SOC unsafe)":"Recovery: ending forced discharge (state or SOC unsafe)","Resumed: monitoring forced discharge after HA restart":"Resumed: monitoring forced discharge after HA restart","Finished: Self-Consumption restored":"Finished: Self-Consumption restored","Paused: Morning Forced Discharge has priority":"Paused: Morning Forced Discharge has priority","ERROR: scene activation failed; retry in 30 seconds":"ERROR: scene activation failed; retry in 30 seconds","ERROR: select Self-Consumption Mode (no battery discharge) in Configure":"ERROR: select Self-Consumption Mode (no battery discharge) in Configure","ERROR: normal Self-Consumption scene unavailable":"ERROR: normal Self-Consumption scene unavailable","ERROR: no unique available Self-Consumption Mode (no battery discharge) scene found":"ERROR: no unique available Self-Consumption Mode (no battery discharge) scene found","ERROR: normal self-consumption scene unavailable; retry pending":"ERROR: normal self-consumption scene unavailable; retry pending","Off: max battery discharge scene activated":"Off: max battery discharge scene activated","Schedule changed: applying selected mode":"Schedule changed: applying selected mode","Discount: no battery discharge scene activated":"Discount: no battery discharge scene activated","Standard: max battery discharge scene activated":"Standard: max battery discharge scene activated","WARNING: discount scene unavailable; using normal Self-Consumption":"WARNING: discount scene unavailable; using normal Self-Consumption","ON":"ON","OFF":"OFF","START":"START","STOP":"STOP","Grid Target: increase in ":"Grid Target: increase in ","Grid Target: decrease in ":"Grid Target: decrease in ","Grid Target: charge set to ":"Grid Target: charge set to ","Scheduled for ":"Scheduled for ","Skipped: SOC ":"Skipped: SOC ",", start threshold ":", start threshold ",", reserve ":", reserve ","Active: forced discharge at ":"Active: forced discharge at ","Active: forced discharge limit set to ":"Active: forced discharge limit set to ","ERROR: requested power outside ":"ERROR: requested power outside "},"ru":{"Grid & Battery Control":"Управление сетью и батареей","Active":"Работает","Stopped":"Остановлено","Grid Export":"Экспорт в сеть","Battery Charge SP":"Лимит зарядки батареи","Grid Target":"Контроль экспорта","Battery Morning Discharge":"Утренняя разрядка","Start Time":"Время начала","Stop SOC: Battery Reserved SoC for Backup (selected in integration options)":"Остановка по резерву SOC, выбранному в настройках интеграции","Morning Discharge":"Утренняя разрядка","Night Tariff Mode":"Ночной тариф","Discount Start":"Начало скидки","Discount End":"Конец скидки","Night Tariff":"Ночной тариф","Discounted starting nights":"Дни начала скидки","During discount: Self-Consumption (no battery discharge). Outside: Self-Consumption (max battery discharge).":"Во время скидки разрядка запрещена; вне скидки обычная самообеспечивающая сцена.","Configure the no-battery-discharge scene in the integration options. Verify the scene really blocks battery discharge.":"Сцена без разрядки определяется автоматически по названию в Home Assistant. Проверьте, что она действительно запрещает разрядку.","Monday":"Пн","Tuesday":"Вт","Wednesday":"Ср","Thursday":"Чт","Friday":"Пт","Saturday":"Сб","Sunday":"Вс","Export Target SP":"Цель экспорта","Export Dead Band":"Допустимое отклонение","Export Delay Time":"Задержка регулировки","Charge Gain SP":"Шаг зарядки","Empty SOC SP":"Порог SOC утром","Battery Forced Discharge Power":"Мощность принудительной разрядки","Желаемая мощность экспорта в сеть. Например, 14 000 Вт.":"Желаемая мощность экспорта в сеть, например 14 000 Вт.","Допустимое отклонение от Export Target в обе стороны. Пока экспорт в этом диапазоне, зарядка не изменяется.":"Допустимое отклонение от цели экспорта в обе стороны. Внутри диапазона лимит зарядки не меняется.","Сколько секунд отклонение должно непрерывно оставаться за пределами Dead Band до одного шага регулировки.":"Сколько секунд экспорт должен находиться за пределами допустимого отклонения перед изменением лимита зарядки.","На сколько ватт увеличивать или уменьшать лимит зарядки после истечения таймера.":"На сколько ватт увеличить или уменьшить лимит зарядки после задержки.","Утром принудительная разрядка запускается, только если фактический SOC выше этого порога и резерва батареи.":"Утренняя разрядка начинается только при SOC выше этого порога и резерва батареи.","Лимит мощности принудительной разрядки. Изменения во время активной разрядки сразу отправляются инвертору.":"Лимит мощности принудительной разрядки. Изменения во время работы немедленно отправляются инвертору.","No-discharge scene is detected automatically by its Home Assistant name. Verify the scene really blocks battery discharge.":"Сцена без разрядки определяется автоматически по имени в Home Assistant. Убедитесь, что она действительно запрещает разрядку.","Off":"Выключено","Not run yet":"Ещё не запускалась","Grid Target: charge at minimum":"Контроль экспорта: лимит зарядки минимальный","Grid Target: charge at maximum":"Контроль экспорта: лимит зарядки максимальный","Grid Target: charge at limit":"Контроль экспорта: достигнут предел зарядки","Grid Target: within dead band":"Контроль экспорта: в пределах допустимого отклонения","Grid Target active":"Контроль экспорта работает","Battery Forced Discharge":"Принудительная разрядка батареи","Waiting for Self-Consumption scene":"Ожидание сцены самообеспечения","Waiting for valid export / charging power":"Ожидание данных экспорта и мощности зарядки","ERROR: charge adjustment failed":"ОШИБКА: не удалось изменить лимит зарядки","ERROR: Self-Consumption scene failed":"ОШИБКА: не удалось включить сцену самообеспечения","ERROR: recovery scene unavailable":"ОШИБКА: сцена возврата недоступна","ERROR: cannot exit forced discharge":"ОШИБКА: невозможно завершить принудительную разрядку","ERROR: SOC unavailable/invalid; reverting mode":"ОШИБКА: SOC недоступен или некорректен; возврат к обычному режиму","Morning discharge command failed":"Ошибка команды утренней разрядки","Cannot start: SOC or backup reserve unavailable":"Запуск невозможен: SOC или резерв батареи недоступен","Not configured: choose Forced Discharge scene and power number in integration options":"Не настроено: выберите сцену принудительной разрядки и регулятор мощности в настройках","ERROR: service call failed; inspect HA logs":"ОШИБКА: команда не выполнена; проверьте журнал HA","ERROR: Forced Discharge power entity unavailable":"ОШИБКА: регулятор мощности разрядки недоступен","ERROR: unsafe SOC/reserve; discharge power not changed":"ОШИБКА: недопустимый SOC/резерв; мощность не изменена","ERROR: failed to update Forced Discharge power":"ОШИБКА: не удалось обновить мощность разрядки","Recovery: ending forced discharge (state or SOC unsafe)":"Восстановление: завершение разрядки (состояние или SOC небезопасны)","Resumed: monitoring forced discharge after HA restart":"После перезапуска HA: контроль принудительной разрядки возобновлён","Finished: Self-Consumption restored":"Завершено: режим самообеспечения восстановлен","Paused: Morning Forced Discharge has priority":"Приостановлено: приоритет у утренней принудительной разрядки","ERROR: scene activation failed; retry in 30 seconds":"ОШИБКА: сцена не активирована; повтор через 30 секунд","ERROR: select Self-Consumption Mode (no battery discharge) in Configure":"ОШИБКА: выберите сцену без разрядки батареи в настройках","ERROR: normal Self-Consumption scene unavailable":"ОШИБКА: обычная сцена самообеспечения недоступна","ERROR: no unique available Self-Consumption Mode (no battery discharge) scene found":"ОШИБКА: не найдена единственная доступная сцена без разрядки батареи","ERROR: normal self-consumption scene unavailable; retry pending":"ОШИБКА: обычная сцена недоступна; запланирован повтор","Off: max battery discharge scene activated":"Выключено: активирована сцена максимальной разрядки","Schedule changed: applying selected mode":"Расписание изменено: применяется выбранный режим","Discount: no battery discharge scene activated":"Скидка: активирована сцена без разрядки батареи","Standard: max battery discharge scene activated":"Обычный тариф: активирована сцена максимальной разрядки","WARNING: discount scene unavailable; using normal Self-Consumption":"ВНИМАНИЕ: сцена скидки недоступна; включён обычный режим","ON":"ВКЛ","OFF":"ВЫКЛ","START":"СТАРТ","STOP":"СТОП","Grid Target: increase in ":"Контроль экспорта: увеличение через ","Grid Target: decrease in ":"Контроль экспорта: уменьшение через ","Grid Target: charge set to ":"Контроль экспорта: лимит зарядки установлен ","Scheduled for ":"Запланировано на ","Skipped: SOC ":"Пропущено: SOC ",", start threshold ":", порог запуска ",", reserve ":", резерв ","Active: forced discharge at ":"Активна принудительная разрядка: ","Active: forced discharge limit set to ":"Активна разрядка: лимит установлен ","ERROR: requested power outside ":"ОШИБКА: мощность вне диапазона "},"he":{"Grid & Battery Control":"בקרת רשת וסוללה","Active":"פעיל","Stopped":"מופסק","Grid Export":"ייצוא לרשת","Battery Charge SP":"מגבלת טעינת סוללה","Grid Target":"יעד ייצוא לרשת","Battery Morning Discharge":"פריקת סוללה בבוקר","Start Time":"שעת התחלה","Stop SOC: Battery Reserved SoC for Backup (selected in integration options)":"עצירה לפי רזרבת SOC שנבחרה בהגדרות","Morning Discharge":"פריקת בוקר","Night Tariff Mode":"תעריף לילה","Discount Start":"תחילת ההנחה","Discount End":"סיום ההנחה","Night Tariff":"תעריף לילה","Discounted starting nights":"ימי תחילת ההנחה","During discount: Self-Consumption (no battery discharge). Outside: Self-Consumption (max battery discharge).":"בשעות ההנחה אין פריקת סוללה; מחוץ להן פועלת סצנת הצריכה העצמית הרגילה.","Configure the no-battery-discharge scene in the integration options. Verify the scene really blocks battery discharge.":"סצנת מניעת פריקה מזוהה אוטומטית לפי השם ב-Home Assistant. ודא שהיא אכן מונעת פריקה.","Monday":"ב׳","Tuesday":"ג׳","Wednesday":"ד׳","Thursday":"ה׳","Friday":"ו׳","Saturday":"ש׳","Sunday":"א׳","Export Target SP":"יעד הספק הייצוא","Export Dead Band":"תחום סטייה מותר","Export Delay Time":"השהיית ויסות","Charge Gain SP":"צעד הספק טעינה","Empty SOC SP":"סף SOC בבוקר","Battery Forced Discharge Power":"הספק פריקה מאולצת","Желаемая мощность экспорта в сеть. Например, 14 000 Вт.":"הספק הייצוא הרצוי לרשת, לדוגמה 14,000 ואט.","Допустимое отклонение от Export Target в обе стороны. Пока экспорт в этом диапазоне, зарядка не изменяется.":"סטייה מותרת מיעד הייצוא לשני הכיוונים. בגבולות התחום הטעינה לא משתנה.","Сколько секунд отклонение должно непрерывно оставаться за пределами Dead Band до одного шага регулировки.":"משך הסטייה הרצופה מחוץ לתחום המותר לפני צעד ויסות.","На сколько ватт увеличивать или уменьшать лимит зарядки после истечения таймера.":"גודל שינוי מגבלת הטעינה בוואט לאחר ההשהיה.","Утром принудительная разрядка запускается, только если фактический SOC выше этого порога и резерва батареи.":"פריקת הבוקר תתחיל רק אם SOC גבוה מהסף הזה ומרזרבת הגיבוי.","Лимит мощности принудительной разрядки. Изменения во время активной разрядки сразу отправляются инвертору.":"מגבלת הספק פריקה מאולצת. שינויים במהלך פריקה נשלחים מיד לממיר.","No-discharge scene is detected automatically by its Home Assistant name. Verify the scene really blocks battery discharge.":"סצנת מניעת פריקה מזוהה אוטומטית לפי שמה ב-Home Assistant. ודא שהיא אכן מונעת פריקה.","Off":"כבוי","Not run yet":"טרם הופעל","Grid Target: charge at minimum":"יעד ייצוא: מגבלת הטעינה במינימום","Grid Target: charge at maximum":"יעד ייצוא: מגבלת הטעינה במקסימום","Grid Target: charge at limit":"יעד ייצוא: הגעה למגבלת הטעינה","Grid Target: within dead band":"יעד ייצוא: בתוך תחום הסטייה המותר","Grid Target active":"בקרת הייצוא פעילה","Battery Forced Discharge":"פריקה מאולצת של הסוללה","Waiting for Self-Consumption scene":"ממתין לסצנת צריכה עצמית","Waiting for valid export / charging power":"ממתין לנתוני ייצוא והספק טעינה","ERROR: charge adjustment failed":"שגיאה: שינוי מגבלת הטעינה נכשל","ERROR: Self-Consumption scene failed":"שגיאה: הפעלת סצנת הצריכה העצמית נכשלה","ERROR: recovery scene unavailable":"שגיאה: סצנת השחזור אינה זמינה","ERROR: cannot exit forced discharge":"שגיאה: לא ניתן לצאת מפריקה מאולצת","ERROR: SOC unavailable/invalid; reverting mode":"שגיאה: נתון SOC חסר או לא תקין; חוזר למצב רגיל","Morning discharge command failed":"פקודת פריקת בוקר נכשלה","Cannot start: SOC or backup reserve unavailable":"לא ניתן להתחיל: נתוני SOC או רזרבת גיבוי חסרים","Not configured: choose Forced Discharge scene and power number in integration options":"לא מוגדר: בחר סצנת פריקה מאולצת ובקר הספק בהגדרות","ERROR: service call failed; inspect HA logs":"שגיאה: הפקודה נכשלה; בדוק את יומן HA","ERROR: Forced Discharge power entity unavailable":"שגיאה: בקר הספק הפריקה אינו זמין","ERROR: unsafe SOC/reserve; discharge power not changed":"שגיאה: SOC או רזרבה לא בטוחים; ההספק לא השתנה","ERROR: failed to update Forced Discharge power":"שגיאה: עדכון הספק הפריקה נכשל","Recovery: ending forced discharge (state or SOC unsafe)":"שחזור: מסיים פריקה מאולצת בגלל מצב או SOC לא בטוחים","Resumed: monitoring forced discharge after HA restart":"לאחר אתחול HA: הניטור של פריקה מאולצת חודש","Finished: Self-Consumption restored":"הסתיים: מצב צריכה עצמית שוחזר","Paused: Morning Forced Discharge has priority":"מושהה: לפריקת הבוקר המאולצת יש עדיפות","ERROR: scene activation failed; retry in 30 seconds":"שגיאה: הפעלת הסצנה נכשלה; ניסיון חוזר בעוד 30 שניות","ERROR: select Self-Consumption Mode (no battery discharge) in Configure":"שגיאה: בחר סצנה ללא פריקת סוללה בהגדרות","ERROR: normal Self-Consumption scene unavailable":"שגיאה: סצנת הצריכה העצמית הרגילה אינה זמינה","ERROR: no unique available Self-Consumption Mode (no battery discharge) scene found":"שגיאה: לא נמצאה סצנה יחידה זמינה ללא פריקת סוללה","ERROR: normal self-consumption scene unavailable; retry pending":"שגיאה: סצנת הצריכה העצמית הרגילה אינה זמינה; יבוצע ניסיון חוזר","Off: max battery discharge scene activated":"כבוי: הופעלה סצנת פריקה מרבית","Schedule changed: applying selected mode":"לוח הזמנים השתנה: המצב שנבחר מופעל","Discount: no battery discharge scene activated":"הנחה: הופעלה סצנה ללא פריקת סוללה","Standard: max battery discharge scene activated":"תעריף רגיל: הופעלה סצנת פריקה מרבית","WARNING: discount scene unavailable; using normal Self-Consumption":"אזהרה: סצנת ההנחה לא זמינה; הופעל מצב צריכה עצמית רגיל","ON":"פועל","OFF":"כבוי","START":"הפעל","STOP":"עצור","Grid Target: increase in ":"יעד ייצוא: הגדלה בעוד ","Grid Target: decrease in ":"יעד ייצוא: הקטנה בעוד ","Grid Target: charge set to ":"יעד ייצוא: מגבלת הטעינה נקבעה ל-","Scheduled for ":"מתוכנן לשעה ","Skipped: SOC ":"דולג: SOC ",", start threshold ":", סף התחלה ",", reserve ":", רזרבה ","Active: forced discharge at ":"פריקה מאולצת פעילה: ","Active: forced discharge limit set to ":"פריקה פעילה: מגבלת ההספק נקבעה ל-","ERROR: requested power outside ":"שגיאה: הספק מחוץ לטווח "}};
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
  _status(value){
    const raw=String(value??"—");
    if(raw==="—")return raw;
    const direct=this._tr(raw);
    if(direct!==raw)return direct;
    const parts=["Grid Target: increase in ","Grid Target: decrease in ","Grid Target: charge set to ","Scheduled for ","Skipped: SOC ",", start threshold ",", reserve ","Active: forced discharge limit set to ","Active: forced discharge at ","ERROR: requested power outside "];
    let out=raw;
    for(const part of parts)out=out.split(part).join(this._tr(part));
    return out;
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
    const tariffOn=this._value("switch.sem_night_tariff")==="on";
    setText("[data-grid-state]",this._tr(this._tr(gridOn?"Active":"Stopped")));
    setText("[data-grid-status]",this._status(this._value("sensor.sem_manager_status")));
    setText("[data-morning-status]",this._tr("Morning Discharge")+": "+this._status(this._value("sensor.sem_morning_discharge_status")));
    setText("[data-tariff-status]",this._tr("Night Tariff")+": "+this._status(this._value("sensor.sem_night_tariff_status")));
    for(const [entityId,isOn,onText,offText] of [
      ["switch.sem_grid_target",gridOn,this._tr("STOP"),this._tr("START")],
      ["switch.sem_morning_discharge",morningOn,this._tr("ON"),this._tr("OFF")],
      ["switch.sem_night_tariff",tariffOn,this._tr("ON"),this._tr("OFF")]
    ]){
      const btn=root.querySelector('[data-switch="'+entityId+'"]');
      if(btn){
        btn.classList.toggle("on",isOn);
        if(btn.textContent!==(isOn?onText:offText))btn.textContent=isOn?onText:offText;
      }
    }
    root.querySelectorAll("[data-day]").forEach(btn=>{const state=this._hass.states[btn.dataset.day];btn.classList.toggle("on",state?.state==="on");btn.disabled=!state || state.state==="unavailable" || state.state==="unknown";});
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
    const days=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
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
      <div class="header"><div><div class="title">Sungrow Energy Manager</div><div class="muted">SEM v${CARD_VERSION} · ${this._tr("Grid & Battery Control")}</div></div><button data-switch="switch.sem_grid_target" class="${gridOn?"on":""}">${this._tr(gridOn?"STOP":"START")}</button></div>
      <div class="stats"><div class="stat" data-stat="export" data-more="${exportId}"><span class="muted">${this._tr("Grid Export")}</span><b>${this._fmt(exportId)} W</b></div><div class="stat" data-stat="charge" data-more="sensor.sungrow_pid_charge_history"><span class="muted">${this._tr("Battery Charge SP")}</span><b>${this._fmt(charging)} W</b></div></div>
      <div class="section"><div class="line"><strong>${this._tr("Grid Target")}</strong><span class="muted" data-grid-state>${this._tr(gridOn?"Active":"Stopped")}</span></div>
      ${settings.slice(0,4).map(i=>input(...i)).join("")}
      <div class="status" data-grid-status>${this._value("sensor.sem_manager_status")}</div></div>
      <div class="section"><div class="line"><strong>${this._tr("Battery Morning Discharge")}</strong><button data-switch="switch.sem_morning_discharge" class="${morningOn?"on":""}">${this._tr(morningOn?"ON":"OFF")}</button></div>
      <label class="setting"><span>${this._tr("Start Time")}</span><div class="edit"><input type="time" data-time="time.sem_morning_start" value="${this._value("time.sem_morning_start").slice(0,5)}"></div></label>
      ${settings.slice(4).map(i=>input(...i)).join("")}
      <div class="muted">${this._tr("Stop SOC: Battery Reserved SoC for Backup (selected in integration options)")}</div><div class="status" data-morning-status>Morning Discharge: ${this._status(this._value("sensor.sem_morning_discharge_status"))}</div></div>
      <div class="section"><div class="line"><strong>${this._tr("Night Tariff Mode")}</strong><button data-switch="switch.sem_night_tariff" class="${tariffOn?"on":""}">${this._tr(tariffOn?"ON":"OFF")}</button></div>
      <div class="muted" style="margin-top:8px">${this._tr("Discounted starting nights")} · Home Assistant</div>
      <div class="days" style="display:flex;gap:5px;flex-wrap:wrap;margin-top:8px">${days.map(day=>`<button data-day="switch.sem_discount_${day.toLowerCase()}" class="${this._value("switch.sem_discount_"+day.toLowerCase())==="on"?"on":""}">${this._tr(day)}</button>`).join("")}</div>
      <label class="setting"><span>${this._tr("Discount Start")}</span><div class="edit"><input type="time" data-time="time.sem_tariff_start" value="${this._value("time.sem_tariff_start").slice(0,5)}"></div></label>
      <label class="setting"><span>${this._tr("Discount End")}</span><div class="edit"><input type="time" data-time="time.sem_tariff_end" value="${this._value("time.sem_tariff_end").slice(0,5)}"></div></label>
      <div class="muted">${this._tr("During discount: Self-Consumption (no battery discharge). Outside: Self-Consumption (max battery discharge).")}</div>
      <div class="status" data-tariff-status>Night Tariff: ${this._status(this._value("sensor.sem_night_tariff_status"))}</div>
      <div class="muted">${this._tr("Configure the no-battery-discharge scene in the integration options. Verify the scene really blocks battery discharge.")}</div></div>
    </ha-card>`;
    this.shadowRoot.querySelectorAll("[data-switch]").forEach(btn=>btn.onclick=async()=>{
      btn.disabled=true;
      try{await this._send("switch",this._value(btn.dataset.switch)==="on"?"turn_off":"turn_on",{entity_id:btn.dataset.switch});}
      catch(e){
        console.error("SEM switch error",e);
        if(btn.dataset.switch==="switch.sem_night_tariff" && /no-battery-discharge scene/i.test(String(e.message))){
          const note=this.shadowRoot.querySelector("[data-tariff-status]");
          const lang=(this._hass?.language||"en").split("-")[0];
          if(note)note.textContent=lang==="ru"?"Ночной тариф не включён: выберите сцену «Self-Consumption Mode (no battery discharge)» в настройках интеграции.":lang==="he"?"תעריף הלילה לא הופעל: בחר סצנה Self-Consumption Mode (no battery discharge) בהגדרות האינטגרציה.":"Night tariff was not enabled: select the Self-Consumption Mode (no battery discharge) scene in integration settings.";
        }else alert("SEM: "+e.message);
      }finally{btn.disabled=false;}
    });
    this.shadowRoot.querySelectorAll("[data-day]").forEach(btn=>btn.onclick=async()=>{
      const entityId=btn.dataset.day;
      if(!this._hass.states[entityId])return;
      btn.disabled=true;
      try{await this._send("switch",this._value(entityId)==="on"?"turn_off":"turn_on",{entity_id:entityId});}
      catch(e){console.error("SEM discount day error",e);alert("SEM: "+e.message);}
      finally{btn.disabled=false;this.updateLive();}
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
