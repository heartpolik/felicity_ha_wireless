"""Felicity battery — local, read-only polling of the Wi-Fi module (TCP 53970)."""
from __future__ import annotations

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .api import FelicityClient
from .coordinator import FelicityConfigEntry, FelicityCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: FelicityConfigEntry) -> bool:
    client = FelicityClient(entry.data[CONF_HOST], entry.data[CONF_PORT])
    coordinator = FelicityCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: FelicityConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload(hass: HomeAssistant, entry: FelicityConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
