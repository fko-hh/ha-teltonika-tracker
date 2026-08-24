"""Sensors for Teltonika Tracker."""

from datetime import date, datetime
from decimal import Decimal

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfSpeed
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Teltonika sensors."""

    manager = entry.runtime_data.manager

    entities = {}

    @callback
    def tracker_updated(tracker):
        """Handle tracker update."""

        # Timestamp
        key = (tracker.imei, "timestamp")

        if key not in entities:
            entity = TeltonikaTimestampSensor(tracker)
            entities[key] = entity
            async_add_entities([entity])
        else:
            entities[key].async_write_ha_state()

        # Speed
        key = (tracker.imei, "speed")

        if key not in entities:
            entity = TeltonikaSpeedSensor(tracker)
            entities[key] = entity
            async_add_entities([entity])
        else:
            entities[key].async_write_ha_state()

        # IO Elements
        for io_id in tracker.io_elements:
            key = (tracker.imei, f"io_{io_id}")

            if key not in entities:
                entity = TeltonikaIOSensor(
                    tracker,
                    io_id,
                )

                entities[key] = entity
                async_add_entities([entity])

            else:
                entities[key].async_write_ha_state()

    manager.add_listener(tracker_updated)

    for tracker in manager.trackers.values():
        tracker_updated(tracker)


class TeltonikaTimestampSensor(SensorEntity):
    """Sensor for the last AVL record timestamp."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_has_entity_name = True
    _attr_name = "Last AVL record"
    _attr_should_poll = False

    def __init__(self, tracker) -> None:
        """Initialize the sensor."""
        self.tracker = tracker

        self._attr_unique_id = f"{tracker.imei}_timestamp"

    @property
    def native_value(
        self,
    ) -> StateType | str | int | float | date | datetime | Decimal | None:
        """Return the timestamp of the last AVL record."""
        return self.tracker.timestamp

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info."""
        return device_info(self.tracker)


class TeltonikaSpeedSensor(SensorEntity):
    """Sensor for the speed of the tracker."""

    _attr_device_class = SensorDeviceClass.SPEED
    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_has_entity_name = True
    _attr_name = "Speed"
    _attr_should_poll = False

    def __init__(self, tracker) -> None:
        """Initialize the sensor."""
        self.tracker = tracker

        self._attr_unique_id = f"{tracker.imei}_speed"

    @property
    def native_value(
        self,
    ) -> StateType | str | int | float | date | datetime | Decimal | None:
        """Return the speed of the tracker."""
        return self.tracker.speed

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info."""
        return device_info(self.tracker)


class TeltonikaIOSensor(SensorEntity):
    """Sensor for an IO element of the tracker."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, tracker, io_id) -> None:
        """Initialize the sensor."""
        self.tracker = tracker
        self.io_id = io_id

        self._attr_unique_id = f"{tracker.imei}_io_{io_id}"

        self._attr_name = self.tracker.io_elements[io_id].name()

    @property
    def native_value(
        self,
    ) -> StateType | str | int | float | date | datetime | Decimal | None:
        """Return the value of the IO element."""
        return self.tracker.io_elements.get(self.io_id).value

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info."""
        return device_info(self.tracker)


def device_info(tracker):
    """Return Home Assistant device info for a tracker."""
    return {
        "identifiers": {(DOMAIN, tracker.imei)},
        "name": f"Tracker {tracker.imei}",
        "manufacturer": "Teltonika Telematics",
    }
