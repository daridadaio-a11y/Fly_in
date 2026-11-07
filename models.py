from dataclasses import dataclass
from typing import TypeAlias
from typing import TypedDict


DroneId: TypeAlias = int
ZoneName: TypeAlias = str
Turn: TypeAlias = int
ZoneAtTurn: TypeAlias = tuple[ZoneName, Turn]

MetadataValue = str | int


class TurnState(TypedDict):
    """1ターン分の移動、位置、使用量、配達数を保持する。"""

    turn: int
    movements: list[str]
    drone_positions: dict[DroneId, tuple[str, ...]]
    zone_usage: dict[ZoneName, int]
    connection_usage: dict[tuple[ZoneName, ZoneName], int]
    delivered_count: int


@dataclass
class Zone:
    """マップ上の1ゾーンと、その役割・座標・メタデータ。"""

    name: str
    role: str
    metadata: dict[str, MetadataValue]
    x: int
    y: int


@dataclass
class Connection:
    """2ゾーン間の無向接続と、その容量メタデータ。"""

    zone1: str
    zone2: str
    metadata: dict[str, MetadataValue]


@dataclass
class MapData:
    """パーサーが生成するドローン数、ゾーン、接続の集合。"""

    total_drones: int
    zones: dict[str, Zone]
    connections: dict[tuple[str, str], Connection]
