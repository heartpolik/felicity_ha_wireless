"""Base entity for Felicity (local Wi-Fi)."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FelicityCoordinator


class FelicityEntity(CoordinatorEntity[FelicityCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: FelicityCoordinator, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        sn = entry.unique_id or entry.entry_id
        basic = coordinator.basic
        # unique_id format kept compatible with the early YAML version of this integration
        self._attr_unique_id = f"felicity_local_{sn}_{key}"
        self._attr_translation_key = key
        sw = basic.get("M1SwVer")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, sn)},
            name="Felicity battery",
            manufacturer="Felicity Solar",
            model=f"Battery (type {basic.get('Type', '?')}/{basic.get('SubType', '?')})",
            serial_number=sn,
            sw_version=f"BMS {sw}" if sw is not None else None,
            hw_version=f"Wi-Fi {basic['version']}" if basic.get("version") else None,
        )
