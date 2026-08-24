"""Device Tracker for Teltonika Tracker."""

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Teltonika device trackers."""

    manager = entry.runtime_data.manager

    entities = {}

    @callback
    def tracker_updated(tracker):
        """Create or update device tracker."""

        entity = entities.get(tracker.imei)

        # Tracker noch nicht vorhanden
        if entity is None:
            entity = TeltonikaDeviceTracker(tracker)

            entities[tracker.imei] = entity

            async_add_entities([entity])

        # Tracker existiert bereits
        else:
            entity.async_write_ha_state()

    manager.add_listener(tracker_updated)

    # Falls beim Laden schon Tracker existieren
    for tracker in manager.trackers.values():
        tracker_updated(tracker)


class TeltonikaDeviceTracker(TrackerEntity):
    """Teltonika GPS tracker."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, tracker) -> None:
        """Initialize the Teltonika device tracker."""
        self.tracker = tracker

        self._attr_unique_id = f"{tracker.imei}_location"
        self._attr_name = "Location"

    @property
    def latitude(self) -> float | None:
        """Return the latitude of the device."""
        return self.tracker.latitude

    @property
    def longitude(self) -> float | None:
        """Return the longitude of the device."""
        return self.tracker.longitude

    @property
    def source_type(self) -> SourceType:
        """Return the source type of the device tracker."""
        return SourceType.GPS

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device information about the tracker."""
        return {
            "identifiers": {(DOMAIN, self.tracker.imei)},
            "name": f"Teltonika {self.tracker.imei}",
            "manufacturer": "Teltonika",
        }

    @property
    def extra_state_attributes(self) -> dict[str, float] | None:
        """Return extra state attributes of the tracker."""
        return {
            "altitude": self.tracker.altitude,
            "satellites": self.tracker.satellites,
            "angle": self.tracker.angle,
        }
