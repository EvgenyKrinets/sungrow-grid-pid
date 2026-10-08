<div align="center">

# ⚡ Sungrow Grid PID v2.0.0

### Контроллер экспорта Sungrow на базе исходной Home Assistant automation

**Версия 2 полностью перестроена вокруг проверенного скрипта `Simple Grid Battery Controller`.**

</div>

## Что изменилось в v2

Интеграция больше не пытается реализовывать отдельную сложную PID-логику. Она повторяет исходный алгоритм:

```text
grid       = sensor.export_power
target     = PID Grid Target
output_old = PID Integral

error      = grid - target
output_new = clamp(output_old + error × 0.10, 0, 25000 W)

number.battery_max_charge_power = output_new
PID Integral                    = output_new
```

Цикл выполняется раз в **1 секунду**. Если предыдущий цикл ещё не завершён, новый пропускается — аналогично `mode: single` и `max_exceeded: silent`.

## Что создаётся автоматически

После установки интеграция сама создаёт все необходимые PID-сущности:

| Сущность | Назначение |
|---|---|
| **PID Grid Controller** | Включение / выключение PID |
| **PID Grid Target** | Желаемая отдача в сеть |
| **PID Integral** | Память предыдущего выхода регулятора |
| **PID Grid Error** | Реальный экспорт минус Grid Target |
| **PID Output** | Текущее задание регулятора |

Внешние сущности Sungrow по умолчанию:

- `sensor.export_power`
- `number.battery_max_charge_power`
- `scene.self_consumption_mode_max_battery_discharge`

Их можно изменить через **Settings → Devices & services → Sungrow Grid PID → Configure**.

## PID Grid Target

`PID Grid Target` создаётся как обычная Number entity интеграции со слайдером.

По умолчанию:

- минимум: **0 W**
- максимум: **17 000 W**
- шаг: **1 000 W**
- начальное значение: **15 000 W**

Минимум, максимум и шаг можно менять через **Configure** у интеграции Sungrow Grid PID.

Значение восстанавливается после перезапуска Home Assistant.

## Компактная карточка

Интеграция автоматически добавляет карточку **Sungrow Grid PID** в каталог карточек Home Assistant.

Карточка показывает:

- PID ON/OFF;
- слайдер PID Grid Target;
- значение во время перемещения слайдера;
- реальный экспорт;
- задание на заряд батареи.

Нажатие на **Grid Target**, **Реальный экспорт** или **Задание зарядки** открывает стандартное окно More Info / History для соответствующей сущности.

## Что происходит при включении PID

Перед запуском контроллера автоматически активируется:

`scene.self_consumption_mode_max_battery_discharge`

После этого запускается цикл регулирования.

При выключении PID цикл просто останавливается. Никакая другая сцена автоматически не активируется.

## Установка

1. HACS → Custom repositories.
2. Добавить `EvgenyKrinets/sungrow-grid-pid` как **Integration**.
3. Установить **Sungrow Grid PID**.
4. Перезапустить Home Assistant.
5. Settings → Devices & services → Add Integration → **Sungrow Grid PID**.
6. Dashboard → Edit → Add card → **Sungrow Grid PID**.

## Важно при переходе со старой automation

Если старая automation **Simple Grid Battery Controller** всё ещё включена, её нужно отключить перед запуском интеграции v2, иначе два регулятора будут одновременно записывать значение в `number.battery_max_charge_power`.

Старые `input_number.pid_grid_target` и `input_number.pid_integral` интеграция не удаляет автоматически. Это сделано намеренно, чтобы не удалять пользовательские helpers без разрешения.

После проверки v2 старые helpers можно удалить вручную, если они больше нигде не используются.

---

<div align="center">

### Sungrow Grid PID · v2.0.0

Основано на исходной проверенной автоматизации.

</div>
