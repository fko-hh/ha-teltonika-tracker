"""Runtime representation of a Teltonika tracker."""

from dataclasses import dataclass, field
from datetime import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .teltonika_codec8_udp_parser import IOElement

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1


@dataclass
class Tracker:
    """Represent one Teltonika tracker."""

    imei: str

    timestamp: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None
    speed: int | None = None
    altitude: int | None = None
    angle: int | None = None
    satellites: int | None = None

    io_elements: dict[int, IOElement] = field(default_factory=dict)

    def update_from_record(self, record) -> None:
        """Update tracker from an AVL record."""

        self.timestamp = record.timestamp
        self.latitude = record.gps.latitude
        self.longitude = record.gps.longitude
        self.speed = record.gps.speed
        self.altitude = record.gps.altitude
        self.angle = record.gps.angle
        self.satellites = record.gps.satellites

        self.io_elements = record.io_elements

    def to_dict(self) -> dict:
        """Return a dictionary representation of the tracker."""
        return {
            "imei": self.imei,
            "timestamp": self.timestamp,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "speed": self.speed,
            "altitude": self.altitude,
            "angle": self.angle,
            "satellites": self.satellites,
            "io_elements": {k: v.__dict__ for k, v in self.io_elements.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> Tracker:
        """Create a Tracker instance from a dictionary."""
        tracker = cls(imei=data["imei"])
        timestamp = data.get("timestamp")
        tracker.timestamp = (
            datetime.fromisoformat(timestamp)
            if isinstance(timestamp, str)
            else timestamp
        )
        tracker.latitude = data.get("latitude")
        tracker.longitude = data.get("longitude")
        tracker.speed = data.get("speed")
        tracker.altitude = data.get("altitude")
        tracker.angle = data.get("angle")
        tracker.satellites = data.get("satellites")

        io_elements_data = data.get("io_elements", {})
        for io_id, io_data in io_elements_data.items():
            io_element = IOElement(
                id=io_data["id"],
                value=io_data["value"],
                size=io_data["size"],
            )
            tracker.io_elements[int(io_id)] = io_element

        return tracker


class TrackerManager:
    """Manage Teltonika trackers."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the tracker manager."""
        self.hass = hass
        self.entry = entry

        self.trackers: dict[str, Tracker] = {}
        self.listeners = []

        self.store = Store(
            hass, STORAGE_VERSION, f"teltonika_tracker_data_{entry.entry_id}"
        )

    async def async_load(self) -> None:
        """Load trackers from storage."""
        data = await self.store.async_load()

        _LOGGER.info("Loaded trackers from storage: %s", data)

        if data is None:
            return

        for tracker_data in data.get("trackers", []):
            tracker = Tracker.from_dict(tracker_data)
            self.trackers[tracker.imei] = tracker
            _LOGGER.info("Loaded tracker: %s", tracker)

    async def async_save(self) -> None:
        """Save trackers to storage."""
        data = {"trackers": [tracker.to_dict() for tracker in self.trackers.values()]}
        await self.store.async_save(data)

    async def update(self, imei: str, record) -> Tracker:
        """Create or update tracker."""

        tracker = self.trackers.get(imei)

        if tracker is None:
            tracker = Tracker(imei=imei)
            self.trackers[imei] = tracker

        tracker.update_from_record(record)

        await self.async_save()

        for listener in self.listeners:
            listener(tracker)

        return tracker

    def add_listener(self, listener) -> None:
        """Add a listener for tracker updates."""
        self.listeners.append(listener)
