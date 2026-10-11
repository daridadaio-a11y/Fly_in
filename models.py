from dataclasses import dataclass
from typing import TypeAlias

DroneId : TypeAlias = int
ZoneName: TypeAlias = str
Turn: TypeAlias = int
MetadataValue = str | int


@dataclass
class Zone:
    name: str
    role: str
    metadata: dict[str, MetadataValue]
    x: int
    y: int


@dataclass
class Connection:
    zone1: str
    zone2: str
    metadata: dict[str, MetadataValue]


@dataclass
class MapData:
    total_drones: int
    zones: dict
    connections: dict[tuple[str, str], Connection]
