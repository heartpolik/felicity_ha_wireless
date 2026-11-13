"""Config flow for Felicity (local Wi-Fi)."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback

from .api import FelicityClient, FelicityError
from .const import (
    CMD_REAL,
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)


async def _probe(host: str, port: int) -> dict[str, Any]:
    return await FelicityClient(host, port).query(CMD_REAL, expect_key="Batsoc")


class FelicityConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                data = await _probe(user_input[CONF_HOST], user_input[CONF_PORT])
            except FelicityError:
                errors["base"] = "cannot_connect"
            else:
                if "Batsoc" not in data:
                    errors["base"] = "not_battery"
                else:
                    sn = str(data.get("DevSN") or data.get("wifiSN") or user_input[CONF_HOST])
                    await self.async_set_unique_id(sn)
                    self._abort_if_unique_id_configured(updates=user_input)
                    return self.async_create_entry(title=f"Felicity {sn[-6:]}", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=(user_input or {}).get(CONF_HOST, "")): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await _probe(user_input[CONF_HOST], user_input[CONF_PORT])
            except FelicityError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(entry, data_updates=user_input)
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): str,
                vol.Required(CONF_PORT, default=entry.data[CONF_PORT]): vol.Coerce(int),
            }
        )
        return self.async_show_form(step_id="reconfigure", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return FelicityOptionsFlow()


class FelicityOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=3600)
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
