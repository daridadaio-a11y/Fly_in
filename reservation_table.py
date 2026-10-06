"""時間付き経路探索で使用する予約表の設計骨組み。

処理コードは含めず、必要な責務、メソッド、判定規則だけを示す。
"""

from graph import Graph


class ReservationTable:
    """ターンごとのゾーン使用数と接続使用数を管理する。

    管理する予定の状態:
        graph: ゾーン容量と接続容量を取得するGraph。
        total_drones: startとgoalの無制限容量に使用する機体数。
        zone_reservations: ``(zone_name, turn)``ごとの予約機体ID。
        connection_reservations: ``(connection_key, turn)``ごとの予約機体ID。
        drone_paths: 予約解除に使う機体IDごとの時間付き経路。

    時間付き経路の各要素は``(location, turn)``とする。locationは
    ゾーン名、またはrestricted移動中の正規化した接続名を表す。
    """

    def __init__(self, graph: Graph, total_drones: int) -> None:
        """空のゾーン予約表、接続予約表、機体別経路を用意する。"""

    def connection_key(self, zone1: str, zone2: str) -> tuple[str, str]:
        """双方向で共有する接続キーを一定の順序で返す。

        ``A-B``と``B-A``を同じ接続として扱い、逆方向の同時使用でも
        max_link_capacityを超えないようにする。
        """

    def can_use_zone(self, zone_name: str, turn: int) -> bool:
        """指定ターンにゾーンをもう1機予約できるか返す。

        startとgoalは容量無制限、それ以外は予約数がmax_drones未満かを
        判定する。blockedは常に使用不可とする。
        """

    def can_use_connection(
        self,
        zone1: str,
        zone2: str,
        turn: int,
    ) -> bool:
        """指定ターンに接続をもう1機予約できるか返す。

        両方向の予約数を合計し、max_link_capacity未満かを判定する。
        """

    def can_reserve_move(
        self,
        source: str,
        destination: str,
        departure_turn: int,
    ) -> bool:
        """1回の移動に必要な全ターンをまとめて予約可能か判定する。

        normal/priorityへの移動では使用接続と到着先を確認する。
        restrictedへの移動では接続の各占有ターンと2ターン後の到着先を
        確認し、到着先を予約できない場合は出発させない。
        """

    def reserve_path(
        self,
        drone_id: int,
        timed_path: list[tuple[str, int]],
    ) -> None:
        """goalまで決まった時間付き経路を予約表へ登録する。

        startでの待機は容量を消費せず、goal到着後は予約を追加しない。
        restricted移動ではゾーンだけでなく接続上の時間も登録する。
        """

    def release_path(self, drone_id: int) -> None:
        """指定機体の全予約を解除し、別経路を探索可能にする。"""

    def clear(self) -> None:
        """すべての予約と機体別経路を初期状態へ戻す。"""
