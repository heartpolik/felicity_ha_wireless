"""Diagnostics: raw replies from the module (serials redacted)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import CMD_SETTINGS
from .coordinator import FelicityConfigEntry

TO_REDACT = {"DevSN", "wifiSN", "host"}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: FelicityConfigEntry) -> dict[str, Any]:
    coordinator = entry.runtime_data
    try:
        settings = await coordinator.client.query(CMD_SETTINGS)
    except Exception as err:  # noqa: BLE001 — diagnostics must not fail
        settings = {"error": str(err)}
    return async_redact_data(
        {
            "entry": dict(entry.data),
            "options": dict(entry.options),
            "basic": coordinator.basic,
            "real": coordinator.data,
            "settings": settings,
        },
        TO_REDACT,
    )
