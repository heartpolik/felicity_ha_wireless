"""Connectivity sensor for Felicity (local Wi-Fi)."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import FelicityConfigEntry
from .entity import FelicityEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: FelicityConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([FelicityLink(entry.runtime_data, "link")])


class FelicityLink(FelicityEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        return True  # this entity *reports* availability, so it is always available

    @property
    def is_on(self) -> bool:
        return self.coordinator.last_update_success
