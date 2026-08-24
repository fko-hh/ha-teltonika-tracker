"""Teltonika Codec8 UDP protocol implementation."""

import asyncio
import logging

from homeassistant.core import HomeAssistant

from .teltonika_codec8_udp_parser import build_codec8_udp_ack, parse_codec8_udp
from .tracker import TrackerManager

_LOGGER = logging.getLogger(__name__)


class Codec8UDPProtocol(asyncio.DatagramProtocol):
    """Codec8 UDP protocol implementation."""

    def __init__(self, hass: HomeAssistant, manager: TrackerManager) -> None:
        """Initialize the protocol."""
        self.transport: asyncio.DatagramTransport | None = None
        self.manager = manager
        self.hass = hass

    def connection_made(self, transport):
        """Handle connection made."""
        _LOGGER.info(
            "Listening for Teltonika Codec8 UDP data on port %s",
            transport.get_extra_info("sockname")[1],
        )
        self.transport = transport

    def datagram_received(self, data, addr):
        """Handle received datagram."""
        _LOGGER.info("Received data from %s: %s", addr, data.hex())
        # Here you would decode the Codec8 data and process it accordingly

        packet = parse_codec8_udp(data)

        _LOGGER.info(packet.imei)

        for record in packet.records:
            _LOGGER.info(record.timestamp)
            _LOGGER.info(record.gps.latitude)
            _LOGGER.info(record.gps.longitude)
            _LOGGER.info(record.gps.speed)

            for io_id, io in record.io_elements.items():
                _LOGGER.info(
                    "IO %s: value=%s, size=%s, name=%s",
                    io_id,
                    io.value,
                    io.size,
                    io.name(),
                )
            # Update the tracker manager with the new record
            self.hass.async_create_task(self.manager.update(packet.imei, record))

        ack = build_codec8_udp_ack(packet)
        self.transport.sendto(ack, addr)
        _LOGGER.info("Send ack for package. ACK Code: %s", ack.hex())

    def error_received(self, exc):
        """Handle error received."""
        _LOGGER.error("Error received: %s", exc)
