"""Vento fan binary sensors."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from ecoventv2 import Fan
from .const import DOMAIN


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the binary sensors platform."""
    async_add_entities(
        [
            VentoBinarySensor(
                hass, config, "_boost_status", "boost_status", True, None
            ),
            VentoBinarySensor(hass, config, "_timer_mode", "timer_mode", True, None),
            VentoBinarySensor(
                hass,
                config,
                "_humidity_sensor_state",
                "humidity_sensor_state",
                True,
                None,
            ),
        ],
    ),
    """

            VentoBinarySensor(
                hass, config, "_relay_sensor_state", "relay_sensor_state", True, None
            ),
            VentoBinarySensor(
                hass, config, "_battery_voltage", "battery_voltage", True, None
            ),
            VentoBinarySensor(
                hass, config, "_relay_status", "relay_status", True, None
            ),
            VentoBinarySensor(
                hass,
                config,
                "_humidity_senzor_state",
                "humidity_sensor_state",
                True,
                None,
            ),
            VentoBinarySensor(
                hass,
                config,
                "_filter_replacement_status",
                "filter_replacement_status",
                True,
                None,
            ),
            VentoBinarySensor(
                hass, config, "_relay_status", "relay_status", True, None
            ),
            VentoBinarySensor(
                hass, config, "_alarm_status", "alarm_status", True, None
            ),
            VentoBinarySensor(
                hass, config, "_cloud_server_state", "cloud_server_state", True, None
            ),
            VentoBinarySensor(
                hass, config, "_humidity_status", "humidity_status", True, None
            ),
            VentoBinarySensor(
                hass, config, "_analogV_status", "analogV_status", True, None
            ),
    """


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Demo config entry."""
    await async_setup_platform(hass, config_entry, async_add_entities)


class VentoBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        name="VentoBinarySensor",
        method=None,
        enable_by_default: bool = False,
        icon: str = "",
        device_class=BinarySensorDeviceClass,
    ) -> None:
        coordinator: DataUpdateCoordinator = hass.data[DOMAIN][config.entry_id]
        super().__init__(coordinator)
        self._fan: Fan = coordinator._fan
        self._attr_unique_id = self._fan.id + name
        self._attr_name = self._fan.name + name
        self._state = None
        self._sensor_type = device_class
        self._attr_entity_registry_enabled_default = enable_by_default
        self._method = getattr(self, method)
        self._attr_icon = icon

    @property
    def is_on(self):
        self._state = self._method() == "on"
        return self._state

    @property
    def should_poll(self):
        """No polling needed for a demo binary sensor."""
        return True

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the class of this sensor."""
        return self._sensor_type

    @property
    def unique_id(self) -> str | None:
        return self._attr_unique_id

    def boost_status(self):
        return self._fan.boost_status

    def timer_mode(self):
        return self._fan.timer_mode

    def humidity_sensor_state(self):
        return self._fan.humidity_sensor_state

    def relay_sensor_state(self):
        return self._fan.relay_sensor_state

    def battery_voltage(self):
        return self._fan.battery_voltage

    def humidity_treshold(self):
        return self._fan.humidity_treshold

    def filter_replacement_status(self):
        return self._fan.filter_replacement_status

    def relay_status(self):
        return self._fan.relay_status

    def alarm_status(self):
        return self._fan.alarm_status

    def cloud_server_state(self):
        return self._fan.cloud_server_state

    def humidity_status(self):
        return self._fan.humidity_status

    def analogV_status(self):
        return self._fan.analogV_status

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._fan.id)},
            #        "name": self._attr_name,
        }
