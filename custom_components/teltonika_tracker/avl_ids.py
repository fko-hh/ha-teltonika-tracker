"""Teltonika AVL I/O definitions."""

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfSpeed,
)


@dataclass(frozen=True)
class AVLDefinition:
    """Definition of a Teltonika AVL I/O element."""

    name: str
    unit: str | None = None
    multiplier: float = 1.0
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    precision: int | None = None


AVL_DEFINITIONS: dict[int, AVLDefinition] = {
    # Digital / state values
    1: AVLDefinition(
        name="Digital Input 1",
        unit=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    21: AVLDefinition(
        name="GSM Signal",
        unit=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    69: AVLDefinition(
        name="GNSS Status",
        unit=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    200: AVLDefinition(
        name="Sleep Mode",
        unit=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    239: AVLDefinition(
        name="Ignition",
        unit=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    240: AVLDefinition(
        name="Movement",
        unit=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # Voltage / current
    66: AVLDefinition(
        name="External Voltage",
        unit=UnitOfElectricPotential.VOLT,
        multiplier=0.001,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        precision=3,
    ),
    67: AVLDefinition(
        name="Battery Voltage",
        unit=UnitOfElectricPotential.VOLT,
        multiplier=0.001,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        precision=3,
    ),
    68: AVLDefinition(
        name="Battery Current",
        unit=UnitOfElectricCurrent.MILLIAMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # Speed
    24: AVLDefinition(
        name="Speed",
        unit=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # Distance
    16: AVLDefinition(
        name="Total Odometer",
        unit=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    199: AVLDefinition(
        name="Trip Odometer",
        unit=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL,
    ),

    # Battery
    113: AVLDefinition(
        name="Battery Level",
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    114: AVLDefinition(
        name="Fuel Level",
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.FUEL,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    181: AVLDefinition(
        name="GNSS PDOP",
        unit=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    182: AVLDefinition(
        name="GNSS HDOP",
        unit=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    241: AVLDefinition(
        name="GNSS VDOP",
        unit=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
}


def get_avl_definition(avl_id: int) -> AVLDefinition:
    """Return definition for an AVL ID."""

    return AVL_DEFINITIONS.get(
        avl_id,
        AVLDefinition(
            name=f"AVL {avl_id}",
        ),
    )


def get_avl_name(avl_id: int) -> str:
    """Return human readable name for an AVL ID."""

    return get_avl_definition(avl_id).name
