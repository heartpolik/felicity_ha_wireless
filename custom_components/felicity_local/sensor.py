"""Sensors for Felicity (local Wi-Fi)."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import BMS_STATES
from .coordinator import FelicityConfigEntry
from .entity import FelicityEntity

INVALID = (65535, 32767, -1)


def pick(d: dict[str, Any], key: str, *idx: int) -> Any:
    v: Any = d.get(key)
    try:
        for i in idx:
            v = v[i]
    except (IndexError, TypeError, KeyError):
        return None
    return None if v is None or v in INVALID else v


def scaled(key: str, div: float, *idx: int) -> Callable[[dict[str, Any]], float | None]:
    def fn(d: dict[str, Any]) -> float | None:
        v = pick(d, key, *idx)
        return None if v is None else round(v / div, 3)

    return fn


def _current(d: dict[str, Any]) -> float | None:
    try:
        i = d["Batt"][1][0]
    except (KeyError, IndexError, TypeError):
        return None
    return None if i is None else round(i / 10, 1)


def _power(d: dict[str, Any]) -> float | None:
    v, i = pick(d, "Batt", 0, 0), _current(d)
    return None if v is None or i is None else round(v / 1000 * i, 1)


def _delta(d: dict[str, Any]) -> int | None:
    mx, mn = pick(d, "BMaxMin", 0, 0), pick(d, "BMaxMin", 0, 1)
    return None if mx is None or mn is None else mx - mn


def _state(d: dict[str, Any]) -> str | None:
    s = d.get("Bstate", d.get("Estate"))
    return None if s is None else BMS_STATES.get(s, "other")


def _cells_attrs(d: dict[str, Any]) -> dict[str, Any]:
    mm = d.get("BMaxMin") or []
    if len(mm) > 1 and len(mm[1]) > 1:
        return {"cell_max_no": mm[1][0] + 1, "cell_min_no": mm[1][1] + 1}
    return {}


@dataclass(frozen=True, kw_only=True)
class FelicitySensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]
    attrs_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


V = UnitOfElectricPotential.VOLT
A = UnitOfElectricCurrent.AMPERE
M = SensorStateClass.MEASUREMENT
DIAG = EntityCategory.DIAGNOSTIC

SENSORS: tuple[FelicitySensorDescription, ...] = (
    FelicitySensorDescription(key="soc", device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE,
                              state_class=M, suggested_display_precision=0, value_fn=scaled("Batsoc", 100, 0, 0)),
    FelicitySensorDescription(key="soh", native_unit_of_measurement=PERCENTAGE, state_class=M,
                              suggested_display_precision=0, value_fn=scaled("Batsoc", 10, 0, 1)),
    FelicitySensorDescription(key="voltage", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=V,
                              state_class=M, suggested_display_precision=2, value_fn=scaled("Batt", 1000, 0, 0)),
    FelicitySensorDescription(key="current", device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=A,
                              state_class=M, suggested_display_precision=1, value_fn=_current),
    FelicitySensorDescription(key="power", device_class=SensorDeviceClass.POWER, native_unit_of_measurement=UnitOfPower.WATT,
                              state_class=M, suggested_display_precision=0, value_fn=_power),
    FelicitySensorDescription(key="temp1", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                              state_class=M, suggested_display_precision=1, value_fn=scaled("BTemp", 10, 0, 0)),
    FelicitySensorDescription(key="temp2", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                              state_class=M, suggested_display_precision=1, value_fn=scaled("BTemp", 10, 0, 1)),
    FelicitySensorDescription(key="cell_max", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=V,
                              state_class=M, suggested_display_precision=3, value_fn=scaled("BMaxMin", 1000, 0, 0)),
    FelicitySensorDescription(key="cell_min", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=V,
                              state_class=M, suggested_display_precision=3, value_fn=scaled("BMaxMin", 1000, 0, 1)),
    FelicitySensorDescription(key="cell_delta", native_unit_of_measurement="mV", state_class=M,
                              suggested_display_precision=0, value_fn=_delta, attrs_fn=_cells_attrs),
    FelicitySensorDescription(key="state", device_class=SensorDeviceClass.ENUM,
                              options=[*BMS_STATES.values(), "other"], value_fn=_state),
    FelicitySensorDescription(key="charge_v_limit", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=V,
                              state_class=M, entity_category=DIAG, value_fn=scaled("LVolCur", 10, 0, 0)),
    FelicitySensorDescription(key="discharge_v_limit", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=V,
                              state_class=M, entity_category=DIAG, value_fn=scaled("LVolCur", 10, 0, 1)),
    FelicitySensorDescription(key="charge_i_limit", device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=A,
                              state_class=M, entity_category=DIAG, value_fn=scaled("LVolCur", 10, 1, 0)),
    FelicitySensorDescription(key="discharge_i_limit", device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=A,
                              state_class=M, entity_category=DIAG, value_fn=scaled("LVolCur", 10, 1, 1)),
    FelicitySensorDescription(key="fault", entity_category=DIAG, value_fn=lambda d: d.get("Bfault")),
    FelicitySensorDescription(key="warning", entity_category=DIAG, value_fn=lambda d: d.get("Bwarn")),
    *(
        FelicitySensorDescription(
            key=f"cell_{n + 1:02d}",
            device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=V, state_class=M,
            suggested_display_precision=3, entity_category=DIAG, value_fn=scaled("BatcelList", 1000, 0, n),
        )
        for n in range(16)
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: FelicityConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    cells = len((coordinator.data.get("BatcelList") or [[]])[0])
    async_add_entities(
        FelicitySensor(coordinator, d)
        for d in SENSORS
        if not d.key.startswith("cell_") or not d.key[5:].isdigit() or int(d.key[5:]) <= cells
    )


class FelicitySensor(FelicityEntity, SensorEntity):
    entity_description: FelicitySensorDescription

    def __init__(self, coordinator, description: FelicitySensorDescription) -> None:
        key = description.key
        super().__init__(coordinator, key)
        self.entity_description = description
        if key.startswith("cell_") and key[5:].isdigit():
            self._attr_translation_key = "cell_n"
            self._attr_translation_placeholders = {"n": str(int(key[5:]))}

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data) if self.coordinator.data else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        fn = self.entity_description.attrs_fn
        return fn(self.coordinator.data) if fn and self.coordinator.data else None
