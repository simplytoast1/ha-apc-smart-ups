"""Binary sensor entities for the APC Smart-UPS (NMC) integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ApcCoordinator, DeviceData
from .entity import ApcEntity


@dataclass(frozen=True, kw_only=True)
class ApcBinarySensorDescription(BinarySensorEntityDescription):
    is_on_fn: Callable[[DeviceData], bool | None]


def _eq(key: str, target: int) -> Callable[[DeviceData], bool | None]:
    """Helper: ``True`` if d[key] == target, ``False`` if d[key] is another
    int, ``None`` if the OID was missing/unsupported. Preserves Unknown so
    the entity reads "Unavailable" instead of falsely "Off"."""
    def fn(d: DeviceData) -> bool | None:
        v = d.get(key)
        return None if v is None else v == target
    return fn


def _fault(d: DeviceData) -> bool | None:
    """Combined fault: battery status in fault, or output in hardware bypass.
    Returns None only if BOTH inputs are unavailable."""
    bs = d.get("battery_status")
    os_ = d.get("output_status")
    if bs is None and os_ is None:
        return None
    return bs == 4 or os_ == 10


BINARY_SENSORS: tuple[ApcBinarySensorDescription, ...] = (
    ApcBinarySensorDescription(
        key="on_battery",
        translation_key="on_battery",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        is_on_fn=_eq("output_status", 3),  # 3 = onBattery
    ),
    ApcBinarySensorDescription(
        key="battery_low",
        translation_key="battery_low",
        device_class=BinarySensorDeviceClass.BATTERY,
        is_on_fn=_eq("battery_status", 3),  # 3 = batteryLow
    ),
    ApcBinarySensorDescription(
        key="battery_needs_replacement",
        translation_key="battery_needs_replacement",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=_eq("battery_replace", 2),
    ),
    ApcBinarySensorDescription(
        key="fault",
        translation_key="fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=_fault,
    ),
    ApcBinarySensorDescription(
        key="online",
        translation_key="online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=_eq("comm_status", 1),
    ),
    ApcBinarySensorDescription(
        key="self_test_passed",
        translation_key="self_test_passed",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda d: (
            None if (v := d.get("test_result")) is None else v != 1
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ApcCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(ApcBinarySensor(coordinator, d) for d in BINARY_SENSORS)


class ApcBinarySensor(ApcEntity, BinarySensorEntity):
    entity_description: ApcBinarySensorDescription

    def __init__(
        self, coordinator: ApcCoordinator, description: ApcBinarySensorDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.unique_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.is_on_fn(self._device)
