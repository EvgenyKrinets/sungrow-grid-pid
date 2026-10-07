<div align="center">

# ⚡ Sungrow Grid PID

### Компактный PID-контроллер экспорта Sungrow для Home Assistant

![Version](https://img.shields.io/badge/version-v1.6.1-0878d1?style=for-the-badge)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41BDF5?style=for-the-badge)
![HACS](https://img.shields.io/badge/HACS-Compatible-7B42BC?style=for-the-badge)

**Держит реальный экспорт около заданного значения и регулирует мощность зарядки батареи.**

</div>

## Что делает интеграция

Контроллер раз в секунду читает реальный экспорт Sungrow, сравнивает его с **PID Grid Target** и изменяет команду максимальной мощности зарядки батареи.

Если экспорт выше цели — разрешённая мощность зарядки увеличивается. Если экспорт ниже цели — уменьшается.

```text
error  = export_power - grid_target
output = previous_output + error × 0.10
output = clamp(output, 0, 25000 W)
```

## Компактная карточка

Встроенная карточка **Sungrow Grid PID** предназначена именно для ежедневного управления и показывает только необходимое:

- переключатель **PID Controller ON/OFF**;
- слайдер **Целевой экспорт**;
- **Реальный экспорт**;
- **Задание на заряд батареи**.

Во время перемещения слайдера новое значение показывается сразу. После отпускания оно записывается в PID Grid Target.

Нажатие на **Целевой экспорт** или его значение открывает стандартное окно Home Assistant для сущности Target. Там доступны история и настройки helper. Минимум, максимум и шаг слайдера задаются в самой сущности PID Grid Target.

Нажатие на **Реальный экспорт** или **Задание на заряд батареи** открывает стандартное окно соответствующей сущности с историей/графиком.

## Что происходит при включении PID

При включении PID интеграция сначала активирует сцену:

`scene.self_consumption_mode_max_battery_discharge`

После этого запускается PID-регулятор и продолжает использовать требуемый режим управления батареей Sungrow.

При обычном выключении PID контроллер останавливается. Текущая версия не активирует другую сцену при выключении.

## Установка через HACS

1. Добавьте `EvgenyKrinets/sungrow-grid-pid` в **HACS → Custom repositories** как **Integration**.
2. Установите **Sungrow Grid PID**.
3. Перезапустите Home Assistant.
4. Добавьте интеграцию **Sungrow Grid PID** в **Settings → Devices & services**.
5. На любом Dashboard выберите **Edit → Add card → Sungrow Grid PID**.

Карточка работает и на телефоне, и на компьютере.

## Сущности

| Сущность | Назначение |
|---|---|
| **PID Grid Controller** | Включение/выключение PID |
| **PID Grid Target** | Желаемый экспорт |
| **PID Output** | Текущая команда регулятора |
| **PID Grid Error** | Отклонение реального экспорта от цели |
| **Sungrow Grid PID Version** | Версия интеграции |

## Требования

- Home Assistant;
- Sungrow iSolarCloud / локальные Sungrow entities;
- сенсор реального export power;
- сущность управления максимальной мощностью зарядки батареи;
- сцена `scene.self_consumption_mode_max_battery_discharge` для автоматической подготовки режима при запуске PID.

## Алгоритм и ограничения

Версия **1.6.1** сохраняет простой алгоритм, уже использовавшийся в исходной Home Assistant automation. Здесь специально не добавлены Search, Import Guard, D-term и другие дополнительные стратегии.

---

<div align="center">

### Sungrow Grid PID · v1.6.1

Компактное управление экспортом и зарядкой батареи.

</div>
