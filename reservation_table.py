from typing import TypeAlias, cast
from graph import Graph
from models import DroneId, ZoneName, Turn, ZoneAtTurn
ConnectionAtTurn: TypeAlias = tuple[ZoneName, ZoneName, Turn]  # 接続元、接続先、予約ターン


class ReservationTable:
    """容量の確認と予約記録を担当する。"""
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        # 各ターン・各ゾーンを予約しているドローンIDを記録
        self.zone_reservations: dict[ZoneAtTurn, set[DroneId]] = {}
        # 各接続・各ターンを予約しているドローンIDを記録
        self.connection_reservations: dict[ConnectionAtTurn, set[DroneId]] = {}

    def can_use_zone(self, zone_name: ZoneName, turn: Turn) -> bool:
        """指定したターンに、指定ゾーンにもう一機予約できるかを判定する。

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
        reservation_drone_ids = self.zone_reservations.get((zone_name, turn), set())
        current_drone_count = len(reservation_drone_ids)
        if current_drone_count < max_drones:
            return True
        return False

    def can_use_connection(self, zone1: ZoneName, zone2: ZoneName, turn: Turn) -> bool:
        """指定したターンに、指定した接続にもう一機予約できるかを判定する。
           両方向を同じ接続として扱い、予約数がmax_link_capacity未満かを判定する。
        """
        connection = self.graph.get_connection(zone1, zone2)
        if connection is None:
            return False
        max_link_capacity = cast(int, connection.metadata["max_link_capacity"])
        reservation_drone_ids = self.connection_reservations.get(
            (connection.zone1, connection.zone2, turn), set())
        current_connection_count = len(reservation_drone_ids)
        if current_connection_count < max_link_capacity:
            return True
        return False


    def reserve_path(
            self,
            path: list[ZoneAtTurn],
            drone_id: DroneId,
    ) -> bool:
        pass


    def reserve_zone(self, zone_name: ZoneName, turn: Turn, drone_id: DroneId) -> bool:
        """引数で指定されたゾーンとターンに引数で渡されたdrone_idを予約登録する関数
           max_droneを確認して使用できれば辞書に追加。
           (zone_name, turn)の集合がなければ、空集合を辞書へ登録。
           その集合へdrone_idを追加。"""
        if self.can_use_zone(zone_name, turn):
            # キーがあれば登録済みの集合を返す
            # キーがなければ空集合を辞書へ登録し、その集合を返す
            reserved_drone_ids = self.zone_reservations.setdefault(
                (zone_name, turn),
                set(), 
                )
            reserved_drone_ids.add(drone_id)
            return True
        return False

    def reserve_connection(self, zone1: ZoneName, zone2: ZoneName, turn: Turn, drone_id: DroneId) -> bool:
        """max_link_capacityを確認して使用できれば辞書に追加。
           (zone_name, zone_name, turn)の集合がなければ、空集合を辞書へ登録。
           その集合へdrone_idを追加。"""
        connection = self.graph.get_connection(zone1, zone2)
        if connection is None:
            return False
        if self.can_use_connection(zone1, zone2, turn):
            reserved_drone_ids = self.connection_reservations.setdefault(
                (
                    connection.zone1,
                    connection.zone2,
                    turn,
                ), set(),
                )
            reserved_drone_ids.add(drone_id)
            return True
        return False
