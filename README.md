# Felicity Wireless (local) for Home Assistant

Read your **Felicity Solar battery** through its built-in Wi-Fi module, locally, with no cloud.
The module listens on TCP port **53970**. The integration polls it every 10 s by default.

The integration only reads. It never sends anything that changes the battery's settings.

> Українською: дивіться [нижче](#українською).

## What you get

| Entity | Notes |
|---|---|
| State of charge, State of health | `%` |
| Voltage, Current, Power | Positive = charging, negative = discharging (BMS convention) |
| Temperature 1 / 2 | BMS temperature probes |
| Cell max / min / delta | Delta in mV, attributes `cell_max_no` / `cell_min_no` |
| Cell 1…16 | Diagnostic, per-cell voltage |
| State | `full`, `standby`, `charging`, `discharging`, `other` |
| Charge / discharge voltage & current limits | What the BMS currently allows (diagnostic) |
| Fault / warning code | Raw BMS codes (diagnostic) |
| Link | Connectivity of the Wi-Fi module |

Diagnostics download includes the raw `real`, `basic` and `settings` replies (serial numbers redacted). Attach them to issues.

## Tested with

- FLB48314TG1-H (16S LiFePO4, 314 Ah) with Wi-Fi firmware 2.15 (`Type 112 / SubType 7353`).

Other Felicity batteries and inverters with the same Wi-Fi module will likely answer too. Reports are welcome.

## Installation (HACS)

1. HACS → ⋮ → **Custom repositories** → `https://github.com/heartpolik/felicity_ha_wireless`, category **Integration**.
2. Install **Felicity Wireless (local)** and restart Home Assistant.
3. **Settings → Devices & services → Add integration → Felicity Wireless (local)** and enter the module IP.

Reserve the module's IP address in your router's DHCP. The module does not announce itself via mDNS.

## Protocol notes

Send the ASCII command and read back one or more JSON objects glued as `{…}{…}`:

| Command | Reply |
|---|---|
| `wifilocalMonitor:get dev real infor` | live data (`Batsoc`, `Batt`, `BatcelList`, `BMaxMin`, `LVolCur`, `BTemp`, `Bstate`, …) |
| `wifilocalMonitor:get dev basice infor` | device / firmware info (the misspelling is the firmware's) |
| `wifilocalMonitor:get dev set infor` | BMS settings (two packets) |

Scaling: `Batt[0][0]` mV · `Batt[1][0]` A×10 · `Batsoc[0] = [SOC×100, SOH×10, ?]` · `BTemp` °C×10 · cells mV · `LVolCur = [[chgV×10, dchgV×10], [chgA×10, dchgA×10]]`.

The protocol was reverse-engineered by the [simon42 community](https://community.simon42.com/t/felicity-solar-per-api-abfragen/42754).

---

## Українською

Локальне читання батареї **Felicity** через її Wi-Fi модуль (TCP 53970), без хмари. Інтеграція тільки читає дані й ніколи не змінює налаштувань батареї.

**Встановлення:**
1. HACS → ⋮ → *Custom repositories* → посилання на цей репозиторій, категорія *Integration*.
2. Встановіть інтеграцію й перезапустіть HA.
3. *Налаштування → Пристрої та служби → Додати інтеграцію* → **Felicity Wireless (local)**, введіть IP модуля.

Закріпіть IP модуля в DHCP роутера.
