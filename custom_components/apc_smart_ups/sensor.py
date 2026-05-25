"""Sensor entities for the APC Smart-UPS (NMC) integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ApcCoordinator, DeviceData
from .entity import ApcEntity
from .oids import BATTERY_STATUS, OUTPUT_STATUS, TEST_RESULT


@dataclass(frozen=True, kw_only=True)
class ApcSensorDescription(SensorEntityDescription):
    value_fn: Callable[[DeviceData], Any]


def _g(key: str) -> Callable[[DeviceData], Any]:
    return lambda d: d.get(key)


SENSORS: tuple[ApcSensorDescription, ...] = (
    ApcSensorDescription(
        key="battery_charge",
        translation_key="battery_charge",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_g("battery_charge"),
    ),
    ApcSensorDescription(
        key="battery_runtime",
        translation_key="battery_runtime",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_g("battery_runtime"),
    ),
    ApcSensorDescription(
        key="battery_voltage",
        translation_key="battery_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_g("battery_voltage"),
    ),
    ApcSensorDescription(
        key="battery_current",
        translation_key="battery_current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_g("battery_current"),
    ),
    ApcSensorDescription(
        key="battery_temperature",
        translation_key="battery_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_g("battery_temp"),
    ),
    ApcSensorDescription(
        key="battery_status",
        translation_key="battery_status",
        device_class=SensorDeviceClass.ENUM,
        options=["unknown", "normal", "low", "fault"],
        value_fn=lambda d: BATTERY_STATUS.get(d.get("battery_status")),
    ),
    ApcSensorDescription(
        key="input_voltage",
        translation_key="input_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_g("input_voltage"),
    ),
    ApcSensorDescription(
        key="input_voltage_max",
        translation_key="input_voltage_max",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_g("input_voltage_max"),
    ),
    ApcSensorDescription(
        key="input_voltage_min",
        translation_key="input_voltage_min",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_g("input_voltage_min"),
    ),
    ApcSensorDescription(
        key="input_frequency",
        translation_key="input_frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_g("input_frequency"),
    ),
    ApcSensorDescription(
        key="output_voltage",
        translation_key="output_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_g("output_voltage"),
    ),
    ApcSensorDescription(
        key="output_current",
        translation_key="output_current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_g("output_current"),
    ),
    ApcSensorDescription(
        key="output_frequency",
        translation_key="output_frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_g("output_frequency"),
    ),
    ApcSensorDescription(
        key="output_load",
        translation_key="output_load",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_g("output_load"),
    ),
    ApcSensorDescription(
        key="output_status",
        translation_key="output_status",
        device_class=SensorDeviceClass.ENUM,
        options=list(OUTPUT_STATUS.values()),
        value_fn=lambda d: OUTPUT_STATUS.get(d.get("output_status")),
    ),
    ApcSensorDescription(
        key="test_result",
        translation_key="test_result",
        device_class=SensorDeviceClass.ENUM,
        options=list(TEST_RESULT.values()),
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: TEST_RESULT.get(d.get("test_result")),
    ),
    ApcSensorDescription(
        key="test_last_date",
        translation_key="test_last_date",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_g("test_last_date"),
    ),
    ApcSensorDescription(
        key="battery_last_replace",
        translation_key="battery_last_replace",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_g("battery_last_replace"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ApcCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(ApcSensor(coordinator, d) for d in SENSORS)


class ApcSensor(ApcEntity, SensorEntity):
    entity_description: ApcSensorDescription

    def __init__(
        self, coordinator: ApcCoordinator, description: ApcSensorDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.unique_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self._device)
