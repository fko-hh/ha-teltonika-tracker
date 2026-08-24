"""The Teltonika Telematics Tracker integration."""

import asyncio
from dataclasses import dataclass
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .teltonika_codec8_udp import Codec8UDPProtocol
from .tracker import TrackerManager

PLATFORMS = [
    Platform.DEVICE_TRACKER,
    Platform.SENSOR,
]

_LOGGER = logging.getLogger(__name__)


@dataclass
class RuntimeData:
    """Runtime data for the Teltonika Telematics Tracker integration."""

    manager: TrackerManager
    transport: asyncio.DatagramTransport


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Teltonika Telematics Tracker from a config entry."""

    port: int = entry.data["port"]

    _LOGGER.info("Setting up Teltonika Telematics Tracker on port %s", port)

    manager = TrackerManager(hass, entry)

    await manager.async_load()

    transport, _ = await hass.loop.create_datagram_endpoint(
        lambda: Codec8UDPProtocol(hass, manager),
        local_addr=("0.0.0.0", port),
    )

    entry.runtime_data = RuntimeData(manager=manager, transport=transport)

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    entry.runtime_data.close()

    return True
