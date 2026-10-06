"""全ドローンの時間付き経路を順番に計画する設計骨組み。"""

from reservation_pathfinder import ReservationPathFinder
from reservation_table import ReservationTable


class PathPlanner:
    """1機ずつ経路探索と予約を行い、全体の運行計画を作る。

    基本版ではD1から順に探索する。後続機が経路を発見できない場合は、
    探索上限の拡大、予約解除、別候補の探索を段階的に試す。
    """

    def __init__(
        self,
        pathfinder: ReservationPathFinder,
        reservations: ReservationTable,
        total_drones: int,
    ) -> None:
        """探索器、共有予約表、計画対象の機体数を保存する。"""

    def plan_all_paths(
        self,
        initial_max_turn: int,
        turn_limit: int,
    ) -> dict[int, list[tuple[str, int]]] | None:
        """全機についてgoalまでの時間付き経路を計画する。

        実装順:
            1. D1から順番に``find_timed_path``を呼ぶ。
            2. 見つかった経路を直ちに予約表へ登録する。
            3. 後続機は登録済みの全予約を避けて探索する。
            4. 失敗時はmax_turnを増やし、全計画をやり直す。
            5. turn_limit以内に全機を計画できなければNoneを返す。

        Challengerで45ターンを破る場合、turn_limitは44にする。
        """

    def plan_one_drone(
        self,
        drone_id: int,
        max_turn: int,
    ) -> list[tuple[str, int]] | None:
        """1機の経路を探索し、成功した場合だけ予約表へ登録する。"""

    def replan_from(
        self,
        drone_id: int,
        max_turn: int,
    ) -> bool:
        """指定機体以降の予約を解除し、別の経路候補を再計画する。

        先行機の貪欲な予約で後続機が詰まった場合の改善点とする。
        最初の必須版では未実装でもよく、HardやChallengerで必要に
        なった段階で追加する。
        """

    def latest_arrival_turn(
        self,
        planned_paths: dict[int, list[tuple[str, int]]],
    ) -> int:
        """全機がgoalへ到着する完了ターンを返す。"""
