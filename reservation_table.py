from typing import TypeAlias, cast
from graph import Graph
from models import DroneId, ZoneName, Turn, ZoneAtTurn
ConnectionAtTurn: TypeAlias = tuple[ZoneName, ZoneName, Turn]  # 接続元、接続先、予約ターン


class ReservationTable:
    """容量の確認と予約記録を担当する。"""
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        # キー：（ゾーン名、ターン）
        # バリュー：その場所を予約しているドローンIDの集合
        self.zone_reservations: dict[ZoneAtTurn, set[DroneId]] = {}
        # キー：（接続元ゾーン、接続先ゾーン）
        # バリュー：その場所を予約しているドローンIDの集合
        self.connection_reservations: dict[ConnectionAtTurn, set[DroneId]] = {}

    def can_use_zone(self, zone_name: ZoneName, turn: Turn) -> bool:
        """指定したターン、指定ゾーンにもう一機予約できるかを判定する。
           
            zone_nameから指定されたゾーンを取得
            max_dronesを取得
            (zone_name, turn)から予約済みドローンIDの集合を取得
            予約済みドローンがmax_drones未満かを判定する

        """
        if zone_name not in self.graph.zones:
            raise ValueError(f"Unknown zone: '{zone_name}'")
        if turn < 0:
            raise ValueError(f"Turn cannot be negative: {turn}")
        zone = self.graph.zones[zone_name]
        if zone.metadata["zone"] == "blocked":
            return False
        if zone.role == "start_hub:" or zone.role == "end_hub:":
            return True
        max_drones = cast(int, zone.metadata["max_drones"])
        # 予約がある場合(キーあり)はドローンID集合を取得する
        # 予約がない場合(キー無し)は空集合を取得し、辞書はできない
        reservation_drone_ids = self.zone_reservations.get((zone_name, turn), set())
        # 現在のゾーン、ターンにいるドローンの数とmax_dronesを比較まだ予約可能か確認
        current_drone_count = len(reservation_drone_ids)
        if current_drone_count < max_drones:
            return True
        return False

    def can_use_connection(self, zone1: ZoneName, zone2: ZoneName, turn: Turn) -> bool:
        """指定したターンに、指定した接続にもう一機予約できるかを判定する。
           両方向を同じ接続として扱い、予約数がmax_link_capacity未満かを判定する。
        """
        if turn < 0:
            raise ValueError(f"Turn cannot be negative: {turn}")
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
            path_list: list[ZoneAtTurn],
            drone_id: DroneId,
    ) -> bool:
        """受け取った完成経路を読み、既存の小さな予約関数を順に呼ぶ"""
        for i in range(len(path_list) - 1):
            previous_state = path_list[i]
            current_state = path_list[i + 1]
            previous_zone, previous_turn = previous_state
            current_zone, current_turn = current_state
            # 待機か移動かを確認する
            if previous_zone == current_zone:
                if not self.reserve_zone(
                    current_zone,
                    current_turn,
                    drone_id
                    ):
                    return False
            else:
                if not self.reserve_connection(
                    previous_zone,
                    current_zone,
                    previous_turn + 1,
                    drone_id,
                    ):
                    return False
                if not self.reserve_zone(
                    current_zone,
                    current_turn,
                    drone_id,
                ):
                    return False
        return True
            
    def reserve_zone(self, zone_name: ZoneName, turn: Turn, drone_id: DroneId) -> bool:
        """引数で指定されたゾーンとターンに引数で渡されたdrone_idを予約登録する関数
           max_droneを確認して使用できれば辞書に追加。
           (zone_name, turn)の集合がなければ、空集合を辞書へ登録。
           その集合へdrone_idを追加。"""
        if self.can_use_zone(zone_name, turn):
            # キーがあれば登録済みの集合を返す
            # キーがなければ空集合を辞書へ登録し、その集合を返す
            # reserved_drone_ids = set()
            reserved_drone_ids = self.zone_reservations.setdefault(
                (zone_name, turn),
                set(), 
                )
            # 同じ集合を指しているので辞書のバリューも変わる
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
            # 同じ集合を指しているので辞書のバリューも変わる
            reserved_drone_ids.add(drone_id)
            return True
        return False
