"""APC Smart-UPS (NMC) integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_COMMUNITY, DOMAIN
from .coordinator import ApcCoordinator
from .snmp_client import ApcSnmpClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    client = ApcSnmpClient(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, 161),
        community=entry.data[CONF_COMMUNITY],
    )

    coordinator = ApcCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: ApcCoordinator | None = hass.data[DOMAIN].pop(entry.entry_id, None)
        if coordinator is not None:
            coordinator.client.shutdown()
    return unload_ok
