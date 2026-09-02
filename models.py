from dataclasses import dataclass


@dataclass
class Zone:
    name: str
    role: str
    metadata: dict
    x: int
    y: int


@dataclass
class Connection:
    zone1: str
    zone2: str
    metadata: dict

@dataclass
class MapData:
    total_drones: int
    zones: dict
    connections: dict