"""Teltonika Codec8 UDP protocol parser implementation."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
import struct

AVL_ID_NAMES: dict[int, str] = {
    1: "DIN1",
    2: "DIN2",
    3: "DIN3",
    9: "Analog Input 1",
    10: "SD Status",
    16: "Total Odometer",
    17: "Axis X",
    18: "Axis Y",
    19: "Axis Z",
    21: "GSM Signal",
    24: "Speed",
    50: "Dallas Temperature 1",
    51: "Dallas Temperature 2",
    52: "Dallas Temperature 3",
    53: "Dallas Temperature 4",
    66: "External Voltage",
    67: "Battery Voltage",
    68: "Battery Current",
    69: "GNSS Status",
    78: "iButton",
    181: "GNSS PDOP",
    182: "GNSS HDOP",
    200: "Sleep Mode",
    239: "Ignition",
    240: "Movement",
    241: "Active GSM Operator",
    249: "Jamming",
}


def get_avl_name(avl_id: int) -> str:
    """Return human-readable AVL IO element name."""
    return AVL_ID_NAMES.get(
        avl_id,
        f"Unknown AVL ID {avl_id}",
    )


class Codec8Error(Exception):
    """Exception raised for errors in the Codec8 UDP protocol."""


class Reader:
    """Helper class to read bytes from a byte array with a cursor."""

    def __init__(self, data: bytes) -> None:
        """Initialize the reader with the given data."""
        self.data = data
        self.pos = 0

    def _read(self, length: int) -> bytes:
        if self.pos + length > len(self.data):
            raise Codec8Error(
                f"Unexpected end of packet at offset {self.pos}, wanted {length} bytes"
            )

        value = self.data[self.pos : self.pos + length]
        self.pos += length
        return value

    def u8(self) -> int:
        """Read an unsigned 8-bit integer from the data."""
        return self._read(1)[0]

    def u16(self) -> int:
        """Read an unsigned 16-bit integer from the data."""
        return struct.unpack(">H", self._read(2))[0]

    def i16(self) -> int:
        """Read a signed 16-bit integer from the data."""
        return struct.unpack(">h", self._read(2))[0]

    def u32(self) -> int:
        """Read an unsigned 32-bit integer from the data."""
        return struct.unpack(">I", self._read(4))[0]

    def i32(self) -> int:
        """Read a signed 32-bit integer from the data."""
        return struct.unpack(">i", self._read(4))[0]

    def u64(self) -> int:
        """Read an unsigned 64-bit integer from the data."""
        return struct.unpack(">Q", self._read(8))[0]

    def bytes(self, length: int) -> bytes:
        """Read the specified number of bytes from the data."""
        return self._read(length)

    @property
    def remaining(self) -> int:
        """Return the number of remaining bytes in the data."""
        return len(self.data) - self.pos


@dataclass
class GPSData:
    """Data class to hold GPS information."""

    longitude: float
    latitude: float
    altitude: int
    angle: int
    satellites: int
    speed: int


@dataclass
class IOElement:
    """Data class to hold IO element information."""

    id: int
    value: int
    size: int

    def name(self) -> str:
        """Return the human-readable name of the IO element."""
        return get_avl_name(self.id)


@dataclass
class AVLRecord:
    """Data class to hold AVL record information."""

    timestamp_ms: int
    timestamp: datetime
    priority: int
    gps: GPSData
    event_io_id: int
    total_io: int
    io_elements: dict[int, IOElement] = field(default_factory=dict)


@dataclass
class Codec8UDPPacket:
    """Data class to hold Codec8 UDP packet information."""

    packet_length: int
    packet_id: int
    avl_packet_id: int
    imei: str
    codec_id: int
    records: list[AVLRecord]


def _parse_io_group(
    reader: Reader,
    size: int,
    io_elements: dict[int, IOElement],
) -> None:
    count = reader.u8()

    for _ in range(count):
        io_id = reader.u8()

        if size == 1:
            value = reader.u8()
        elif size == 2:
            value = reader.u16()
        elif size == 4:
            value = reader.u32()
        elif size == 8:
            value = reader.u64()
        else:
            raise Codec8Error(f"Unsupported IO size: {size}")

        io_elements[io_id] = IOElement(id=io_id, value=value, size=size)


def _parse_record(reader: Reader) -> AVLRecord:
    timestamp_ms = reader.u64()

    priority = reader.u8()

    # Teltonika coordinates are signed integers,
    # scaled by 10,000,000.
    longitude = reader.i32() / 10_000_000
    latitude = reader.i32() / 10_000_000

    altitude = reader.i16()
    angle = reader.u16()
    satellites = reader.u8()
    speed = reader.u16()

    gps = GPSData(
        longitude=longitude,
        latitude=latitude,
        altitude=altitude,
        angle=angle,
        satellites=satellites,
        speed=speed,
    )

    event_io_id = reader.u8()
    total_io = reader.u8()

    io_elements: dict[int, IOElement] = {}

    _parse_io_group(reader, 1, io_elements)
    _parse_io_group(reader, 2, io_elements)
    _parse_io_group(reader, 4, io_elements)
    _parse_io_group(reader, 8, io_elements)

    return AVLRecord(
        timestamp_ms=timestamp_ms,
        timestamp=datetime.fromtimestamp(
            timestamp_ms / 1000,
            tz=UTC,
        ),
        priority=priority,
        gps=gps,
        event_io_id=event_io_id,
        total_io=total_io,
        io_elements=io_elements,
    )


def parse_codec8_udp(data: bytes) -> Codec8UDPPacket:
    """Parse a Codec8 UDP packet from the given data."""
    reader = Reader(data)

    packet_length = reader.u16()
    packet_id = reader.u16()

    not_usable = reader.u8()

    if not_usable != 0x01:
        raise Codec8Error(f"Expected unused byte 0x01, got 0x{not_usable:02X}")

    avl_packet_id = reader.u8()

    imei_length = reader.u16()

    imei_bytes = reader.bytes(imei_length)

    try:
        imei = imei_bytes.decode("ascii")
    except UnicodeDecodeError as err:
        raise Codec8Error("IMEI is not valid ASCII") from err

    codec_id = reader.u8()

    if codec_id != 0x08:
        raise Codec8Error(
            f"Unsupported codec 0x{codec_id:02X}; expected Codec 8 (0x08)"
        )

    record_count = reader.u8()

    records = [_parse_record(reader) for _ in range(record_count)]

    # Codec 8 repeats the record count at the end.
    record_count_2 = reader.u8()

    if record_count != record_count_2:
        raise Codec8Error(f"Record count mismatch: {record_count} != {record_count_2}")

    if reader.remaining:
        raise Codec8Error(f"Unexpected {reader.remaining} trailing bytes")

    return Codec8UDPPacket(
        packet_length=packet_length,
        packet_id=packet_id,
        avl_packet_id=avl_packet_id,
        imei=imei,
        codec_id=codec_id,
        records=records,
    )


def build_codec8_udp_ack(packet: Codec8UDPPacket) -> bytes:
    """Build UDP ACK.

    2 bytes length
    2 bytes packet ID
    1 byte  0x01
    1 byte  AVL packet ID
    1 byte  number of accepted AVL records
    """

    accepted = len(packet.records)

    return struct.pack(
        ">HHBBB",
        5,
        packet.packet_id,
        0x01,
        packet.avl_packet_id,
        accepted,
    )
