"""予約表を避けて1機分の時間付き経路を探す設計骨組み。"""

from graph import Graph
from ゴミ.reservation_table import ReservationTable


class ReservationPathFinder:
    """``(zone_name, turn)``を状態として予約済み場所を避ける探索器。"""

    def __init__(self, graph: Graph) -> None:
        """ゾーン、接続、移動コストを保持するGraphを保存する。"""

    def find_timed_path(
        self,
        start_name: str,
        end_name: str,
        reservations: ReservationTable,
        start_turn: int,
        max_turn: int,
    ) -> list[tuple[str, int]] | None:
        """予約を避け、指定区間のgoalまでの時間付き経路を探す。

        Args:
            start_name: 探索を開始するゾーン名。
            end_name: 到着対象のゾーン名。
            reservations: 先行ドローンが登録済みの予約表。
            start_turn: startにいる最初のターン。
            max_turn: 探索を打ち切る最大ターン。

        探索状態:
            ``(zone_name, turn)``を1状態とする。同じゾーンでもターンが
            違えば別状態として扱う。

        探索候補:
            隣接ゾーンへの移動、現在ゾーンでの待機、restrictedへの
            2ターン移動を含める。blocked、容量超過、max_turn超過は除く。

        評価順:
            到着見込みターンが小さい候補を優先する。同評価なら
            priorityを多く通る候補を優先する。

        Returns:
            ``(location, turn)``を開始地点からgoalまで並べた経路。
            max_turn以内に予約可能な経路がなければNone。
        """

    def _get_move_candidates(
        self,
        zone_name: str,
        turn: int,
        reservations: ReservationTable,
        max_turn: int,
    ) -> list[tuple[str, int]]:
        """移動、待機、restricted移動から予約可能な次状態を作る。"""

    def _estimate_remaining_turns(
        self,
        zone_name: str,
        end_name: str,
    ) -> int:
        """現在地からgoalまでの予約を無視した推定残り時間を返す。"""

    def _reconstruct_path(
        self,
        previous_state: dict[tuple[str, int], tuple[str, int] | None],
        goal_state: tuple[str, int],
    ) -> list[tuple[str, int]]:
        """goalから直前状態を逆にたどり、時間付き経路を復元する。"""
