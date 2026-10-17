"""一機分の完成経路を作る"""

import heapq
from graph import Graph
from reservation_table import ReservationTable
from models import ZoneName, Turn, ZoneAtTurn

class ReservationPathFinder:
    """``(zone_name, turn)``を状態として予約済み場所を避ける探索器。"""

    def __init__(self, graph: Graph) -> None:
        """ゾーン、接続、移動コストを保持するGraphを保存する。"""
        self.graph = graph

    def find_timed_path(
        self,
        start_name: ZoneName,
        end_name: ZoneName,
        reservations: ReservationTable,
        start_turn: Turn,
        max_turn: Turn,
    ) -> list[tuple[str, int]] | None:
        """予約済みの容量を避けて、一機分の時間付き経路を探す。

        (zone_name, turn)を探索状態とし、到着ターンが早い状態から調べる。
        到着ターンが同じ場合はpriorityゾーンを多く通る経路を優先する。

        各状態から、隣接ゾーンへの移動と1ターンの待機をそれぞれ候補にする。
        max_drones, max_link_capacityを超える候補、到着ターンがmax_turnを超える候補は探索対象外。

        goalへ到着後previous_stateを逆にたどり経路を返す。
        max_turn以内に到着できない場合Noneを返す。
        """
        # 開始ゾーンと開始ターンを探索開始時の状態としてまとめる。
        start_state: ZoneAtTurn = (start_name, start_turn)
        # 探索開始時点ではpriorityゾーンを一つも通過してない。
        # priorityゾーンへ入るたびに値を1減らす。
        start_priority = 0
        # (ゾーン名、ターン数)：priority
        best_priority_by_state: dict[ZoneAtTurn, int] = {start_state: start_priority}
        # 到着ターン、priority、現在のゾーン名を持つ探索候補
        search_queue: list[tuple[Turn, int, ZoneName]] = [(start_turn, start_priority, start_name)]
        # キー：到達したゾーン名、ターン
        # バリュー：一つ前の到達したゾーン名、ターン
        previous_state: dict[ZoneAtTurn, ZoneAtTurn | None] = {start_state: None}
        # ループ後にgoal_stateを確認するために初期化
        goal_state: ZoneAtTurn | None = None

        while search_queue:
            current_turn, current_priority, current_name = heapq.heappop(search_queue)
            current_state = (current_name, current_turn)
            # 同じ状態のときにpriorityを比較する。
            if current_priority > best_priority_by_state[current_state]:
                continue
            if current_name == end_name:
                goal_state = current_state
                break
            # 今のゾーンから予約可能な隣接ゾーン、待機がはいっている
            candidates = self._get_move_candidates(
                current_name,
                current_turn,
                reservations,
                max_turn,
                )
            # 待機先または移動先の候補、その場所にいるターンが各々入る
            for candidate_name, candidate_turn in candidates:
                candidate_state = (candidate_name, candidate_turn)
                candidate_priority = current_priority
                metadata = self.graph.zones[candidate_name].metadata
                # 候補のゾーン名が現在地と違うとき
                if candidate_name != current_name and\
                metadata["zone"] == "priority":
                    candidate_priority -= 1
                # 同じゾーン名、同じターンのときに既出priorityより大きいか見る
                known_priority = best_priority_by_state.get(candidate_state)
                if known_priority is None or known_priority > candidate_priority:
                    best_priority_by_state[candidate_state] = candidate_priority
                    previous_state[candidate_state] = current_state
                    heapq.heappush(search_queue,
                                   (candidate_turn, candidate_priority, candidate_name),
                                   )

        if goal_state is None:
            return None
        
        shortestpath = self._reconstruct_path(previous_state, goal_state)
        return shortestpath


    def _get_move_candidates(
        self,
        zone_name: ZoneName,
        turn: Turn,
        reservations: ReservationTable,
        max_turn: int,
    ) -> list[tuple[str, int]]:
        """移動、待機、restricted移動から予約可能な候補リストを作る"""
        candidates: list[ZoneAtTurn] = []
        next_turn = turn + 1
        if next_turn > max_turn:
           return candidates
        # 現在のゾーンで次ターン待機可能か確認
        if reservations.can_use_zone(zone_name, next_turn):
            candidates.append((zone_name, next_turn))
        for neighbor in self.graph.get_neighbors(zone_name):
            neighbor_name = neighbor.name
            movement = self.graph.get_movement_cost(neighbor_name)
            # 接続上のターン
            connection_turn = turn + 1
            # 隣接ゾーンに到着するときのターン
            arrival_turn = turn + movement
            # goalに到着する一番遅いターンを超えたら除外
            if arrival_turn > max_turn:
                continue
            # そのターンに実際空きがあるか確認
            if reservations.can_use_zone(neighbor_name, arrival_turn) and\
            reservations.can_use_connection(zone_name, neighbor_name, connection_turn):
                candidates.append((neighbor_name, arrival_turn))
                
        return candidates


    def _reconstruct_path(
        self,
        previous_state: dict[tuple[str, int], tuple[str, int] | None],
        goal_state: tuple[str, int],
    ) -> list[tuple[str, int]]:
        """goalから直前状態を逆にたどり、時間付き経路を復元する。"""
        shortest_state = []
        path_state: ZoneAtTurn | None = goal_state
        while path_state is not None:
            shortest_state.append(path_state)
            # 終了ゾーンからprevious_state情報を逆向きにたどる
            path_state = previous_state[path_state]
        shortest_state.reverse()
        return shortest_state
