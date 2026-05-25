"""DataUpdateCoordinator for the APC NMC SNMP integration."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .oids import ALL_OIDS
from .snmp_client import ApcSnmpClient, SnmpAuthError, SnmpTransportError

_LOGGER = logging.getLogger(__name__)


@dataclass
class DeviceData:
    """One UPS's poll snapshot. Single-device per config entry for now."""

    values: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        v = self.values.get(key)
        return default if v is None else v


@dataclass
class CoordinatorData:
    device: DeviceData = field(default_factory=DeviceData)


class ApcCoordinator(DataUpdateCoordinator[CoordinatorData]):
    """Polls the configured NMC over SNMP."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: ApcSnmpClient,
    ) -> None:
        interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )
        self.entry = entry
        self.client = client

    async def _async_update_data(self) -> CoordinatorData:
        oids = [oid for (oid, _cast) in ALL_OIDS.values()]
        try:
            raw = await self.client.get(oids)
        except SnmpAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except SnmpTransportError as err:
            raise UpdateFailed(str(err)) from err

        values: dict[str, Any] = {}
        for name, (oid, cast) in ALL_OIDS.items():
            raw_v = raw.get(oid)
            values[name] = _cast(raw_v, cast)

        return CoordinatorData(device=DeviceData(values=values))


def _cast(raw: Any, kind: str) -> Any:
    if raw is None:
        return None
    if kind == "str":
        s = str(raw).strip()
        return s or None
    if kind == "int":
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None
    if kind == "timeticks":
        # SNMP TimeTicks are in hundredths of a second. Convert to seconds.
        try:
            return int(raw) / 100
        except (TypeError, ValueError):
            return None
    return raw
