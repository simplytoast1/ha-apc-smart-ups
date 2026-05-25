"""Base entity for APC Smart-UPS (NMC) integration."""
from __future__ import annotations

from typing import Any

from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import ApcCoordinator, DeviceData


class ApcEntity(CoordinatorEntity[ApcCoordinator]):
    """Shared base for all entities on a single NMC."""

    _attr_has_entity_name = True

    @property
    def _device(self) -> DeviceData:
        return self.coordinator.data.device

    def _v(self, key: str) -> Any:
        return self._device.get(key)

    @property
    def device_info(self) -> DeviceInfo:
        serial = self._v("serial") or self.coordinator.entry.unique_id or "unknown"
        return DeviceInfo(
            identifiers={(DOMAIN, str(serial))},
            manufacturer=MANUFACTURER,
            model=self._v("model"),
            name=self._v("ups_name") or self._v("model") or "Smart-UPS",
            serial_number=self._v("serial"),
            sw_version=self._v("firmware"),
            configuration_url=f"http://{self.coordinator.entry.data.get(CONF_HOST)}/",
        )
