"""Config flow for the APC Smart-UPS (NMC) integration."""
from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    CONF_COMMUNITY,
    DEFAULT_COMMUNITY,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .oids import OID_MODEL, OID_NAME, OID_SERIAL
from .snmp_client import ApcSnmpClient, SnmpAuthError, SnmpTransportError

_LOGGER = logging.getLogger(__name__)


def _schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, "")): str,
            vol.Required(CONF_PORT, default=defaults.get(CONF_PORT, DEFAULT_PORT)): int,
            vol.Required(
                CONF_COMMUNITY, default=defaults.get(CONF_COMMUNITY, DEFAULT_COMMUNITY)
            ): str,
        }
    )


async def _validate(data: dict[str, Any]) -> dict[str, str]:
    """Build a client from form input and probe the NMC. Returns identity dict."""
    client = ApcSnmpClient(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        community=data[CONF_COMMUNITY],
    )
    result = await client.get([OID_MODEL, OID_NAME, OID_SERIAL])
    return {
        "model": str(result.get(OID_MODEL) or "").strip() or "Smart-UPS",
        "name": str(result.get(OID_NAME) or "").strip() or "Smart-UPS",
        "serial": str(result.get(OID_SERIAL) or "").strip() or data[CONF_HOST],
    }


class ApcConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return ApcOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                identity = await _validate(user_input)
            except SnmpAuthError:
                errors["base"] = "invalid_auth"
            except SnmpTransportError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("unexpected error during config-flow probe")
                errors["base"] = "unknown"
            else:
                unique_id = (
                    identity["serial"]
                    or f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                )
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured(
                    updates={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PORT: user_input[CONF_PORT],
                    }
                )
                return self.async_create_entry(
                    title=identity["name"] or identity["model"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=_schema(), errors=errors
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> config_entries.ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()
        schema = _schema(defaults=dict(entry.data))

        if user_input is not None:
            try:
                await _validate(user_input)
            except SnmpAuthError:
                errors["base"] = "invalid_auth"
            except SnmpTransportError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(entry, data=user_input)

        return self.async_show_form(
            step_id="reauth_confirm", data_schema=schema, errors=errors
        )


class ApcOptionsFlow(OptionsFlow):
    """Lets the user adjust runtime settings (poll interval) without re-adding
    the integration."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry_id = config_entry.entry_id

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        current = (
            entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            if entry
            else DEFAULT_SCAN_INTERVAL
        )

        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL])},
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=current
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_SCAN_INTERVAL,
                            max=MAX_SCAN_INTERVAL,
                            step=1,
                            unit_of_measurement="seconds",
                            mode=NumberSelectorMode.SLIDER,
                        )
                    ),
                }
            ),
        )
