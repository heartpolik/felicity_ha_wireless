"""Data update coordinator for Felicity (local Wi-Fi)."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FelicityClient, FelicityError
from .const import CMD_BASIC, CMD_REAL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

type FelicityConfigEntry = ConfigEntry[FelicityCoordinator]


class FelicityCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls ``get dev real infor``; ``basice infor`` is read once for device info."""

    config_entry: FelicityConfigEntry

    def __init__(self, hass: HomeAssistant, entry: FelicityConfigEntry, client: FelicityClient) -> None:
        interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )
        self.client = client
        self.basic: dict[str, Any] = {}

    async def _async_setup(self) -> None:
        try:
            self.basic = await self.client.query(CMD_BASIC, expect_key="DevSN")
        except FelicityError as err:
            _LOGGER.debug("basic info not available: %s", err)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.query(CMD_REAL, expect_key="Batsoc")
        except FelicityError as err:
            raise UpdateFailed(str(err)) from err
