from typing import TypeAlias, cast
from graph import Graph

ZoneName: TypeAlias = str
Turn: TypeAlias = int
DroneId: TypeAlias = int  # ドローン一機のID
ZoneAtTurn: TypeAlias = tuple[ZoneName, Turn]  # ゾーン名、予約ターン
ConnectionAtTurn: TypeAlias = tuple[ZoneName, ZoneName, Turn]  # 接続元、接続先、予約ターン

class ReservationTable:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        # 各ターン・各ゾーンを予約しているドローンIDを記録
        self.zone_reservations: dict[ZoneAtTurn, set[DroneId]] = {}
        # 各接続・各ターンを予約しているドローンIDを記録
        self.connection_reservations: dict[ConnectionAtTurn, set[DroneId]] = {}

    def can_use_zone(self, zone_name: str, turn: int) -> bool:

        """指定したターンに、指定ゾーンをもう一機予約できるかを判定する。

            zone_nameから指定されたゾーンを取得
            max_dronesを取得
            (zone_name, turn)から予約済みドローンIDの集合を取得
            不正なzone_name,負のturnは呼び出し側で防ぐ

        """
        zone = self.graph.zones[zone_name]
        if zone.metadata["zone"] == "blocked":
            return False
        if zone.role == "start_hub:" or zone.role == "end_hub:":
            return True
        max_drones = cast(int, zone.metadata["max_drones"])
        # 予約がある場合はそのドローンID集合を取得する
        # 予約がない場合は空集合を取得する
        droneid = self.zone_reservations.get((zone_name, turn), set())
        current_drone_count = len(droneid)
        if current_drone_count < max_drones:
            return True
        return False