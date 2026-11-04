from dataclasses import dataclass
from typing import TypeAlias
from typing import TypedDict


DroneId: TypeAlias = int
ZoneName: TypeAlias = str
Turn: TypeAlias = int
ZoneAtTurn: TypeAlias = tuple[ZoneName, Turn]

MetadataValue = str | int


class TurnState(TypedDict):
    turn: int
    movements: list[str]
    drone_positions: dict[DroneId, tuple[str, ...]]
    zone_usage: dict[ZoneName, int]
    connection_usage: dict[tuple[ZoneName, ZoneName], int]
    delivered_count: int


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
