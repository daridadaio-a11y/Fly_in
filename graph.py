"""MapDataから経路探索に使用するグラフ構造を作るモジュール。"""

from models import Connection, MapData, Zone


class Graph:
    """ゾーンと接続を、探索しやすい隣接リストとして管理する。

    Parserが生成したMapDataを受け取り、各ゾーンから利用可能な接続を
    取得できる形に変換する。経路探索やシミュレーションは、このクラスを
    通してゾーン、接続、移動コストなどの情報を参照する。
    """
    def __init__(self, map_data: MapData) -> None:
        """MapDataを受け取り、グラフの初期状態を作る。

        Args:
            map_data: ドローン数、ゾーン、接続を保持するマップ情報。
        """
        self.zones = map_data.zones
        self.connections = map_data.connections
        self.adjacency = self._build_adjacency()

    def _build_adjacency(self) -> dict[str, list[Connection]]:
        """すべてのゾーンについて双方向の隣接リストを作る。
        各Connectionをzone1側とzone2側の両方に登録する。接続されて
        いないゾーンも、空のリストを持つキーとして登録する。
        Returns:
            ゾーン名をキー、そこから利用できるConnectionのリストを値と
            する辞書。
        """
        # 接続がないゾーンにも空リストを用意
        adjacency: dict[str, list[Connection]] = {}
        for zone_name in self.zones:
            adjacency[zone_name] = []

        # 各接続を両方のゾーンに登録
        for connection in self.connections.values():
            adjacency[connection.zone1].append(connection)
            adjacency[connection.zone2].append(connection)
        return adjacency

    def get_neighbors(self, zone_name: str) -> list[Zone]:
        """指定したゾーンから直接移動できる隣接ゾーンを取得する。

        blockedゾーンは移動先として返さないことを想定している。

        Args:
            zone_name: 移動元となるゾーンの名前。

        Returns:
            接続によって隣接している、進入可能なZoneのリスト。

        Raises:
            KeyError: 指定されたゾーンが存在しない場合。
        """
        neighbors = []
        for connection in self.adjacency[zone_name]:
            if zone_name == connection.zone1:
                neighbor_zone = self.zones[connection.zone2]
            else:
                neighbor_zone = self.zones[connection.zone1]
            if neighbor_zone.metadata["zone"] != "blocked":
                neighbors.append(neighbor_zone)
        return neighbors

    def get_connection(
        self,
        zone1: str,
        zone2: str,
    ) -> Connection | None:
        """2つのゾーンを結ぶ接続を取得する。

        Args:
            zone1: 一方のゾーン名。
            zone2: もう一方のゾーン名。

        Returns:
            2ゾーン間のConnection。接続が存在しない場合はNone。
        """
        if zone1 < zone2:
            connection = self.connections.get((zone1, zone2))
        else:
            connection = self.connections.get((zone2, zone1))
        return connection

    def get_start_zone(self) -> Zone:
        """マップ内でstart_hubとして定義されたゾーンを取得する。

        Returns:
            ドローンの出発地点となるZone。

        Raises:
            ValueError: start_hubが存在しない場合。
        """
        for zone in self.zones.values():
            if zone.role == "start_hub:":
                return zone
        raise ValueError("Start hub is not defined.")

    def get_end_zone(self) -> Zone:
        """マップ内でend_hubとして定義されたゾーンを取得する。

        Returns:
            ドローンの目的地となるZone。

        Raises:
            ValueError: end_hubが存在しない場合。
        """
        for zone in self.zones.values():
            if zone.role == "end_hub:":
                return zone
        raise ValueError("End hub is not defined.")

    def get_movement_cost(self, zone_name: str) -> int:
        """指定したゾーンへ進入するために必要なターン数を返す。

        normalとpriorityは1ターン、restrictedは2ターンを想定する。
        blockedは進入できないため、経路探索の対象から除外する。

        Args:
            zone_name: 移動先となるゾーンの名前。

        Returns:
            移動先へ到着するまでに必要なターン数。

        Raises:
            KeyError: 指定されたゾーンが存在しない場合。
            ValueError: 指定されたゾーンがblockedの場合。
        """
        zone = self.zones[zone_name]
        zone_type = zone.metadata["zone"]
        if zone_type == "blocked":
            raise ValueError(f"Cannot enter blocked zone '{zone_name}'.")
        if zone_type == "restricted":
            return 2
        if zone_type == "normal" or zone_type == "priority":
            return 1
        raise ValueError(f"Unknown zone type '{zone_type}'.")
        