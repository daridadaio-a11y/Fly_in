"""ReservationPathを全機分繰り返して予約する"""

from graph import Graph
from reservation_table import ReservationTable
from reservation_pathfinder import ReservationPathFinder
from pathfinding import PathFinder
from models import DroneId, ZoneAtTurn

class PathPlanner:
    """ドローンIDを1から順に取り出す
    → ReservationPathFinderで完成経路を探す
    → その完成経路をdrone_id付きで予約する
    → 経路を保存する"""
    def __init__(
            self,
            graph: Graph,
            total_drones: int,
            ):
        self.graph = graph
        self.total_drones = total_drones
            
    def plan_all(self) -> dict[DroneId, list[ZoneAtTurn]]:
        """理論上の最大ターン数を超えないように
        探索ｰ>reserve_pathで経路を予約ｰ>planned_pathsへ保存、を繰り返す"""
        # ローカル変数にすることにより何度呼び出しても同じ結果になる
        reservations = ReservationTable(self.graph)
        reservation_pathfinder = ReservationPathFinder(self.graph)
        pathfinder = PathFinder(self.graph)
        planned_paths: dict[DroneId, list[ZoneAtTurn]] = {}

        start_name = self.graph.get_start_zone().name
        end_name = self.graph.get_end_zone().name
        # 予約なしの場合の最短ターン
        result = pathfinder.find_shortest_path(
            start_name,
            end_name,
        )
        if result is None:
            raise RuntimeError(
                f"No path exists from '{start_name}' to '{end_name}'."
            )
        _shortest_path, score = result
        shortest_turns, _priority = score
        for drone_id in range(1, self.total_drones + 1):
            # 各ドローンの理論上最大ターン
            max_turn = shortest_turns + (drone_id - 1)
            # 予約済みの容量を避けて、一機分の時間付き経路を探す
            path_list = reservation_pathfinder.find_timed_path(
                start_name,
                end_name,
                reservations,
                0,
                max_turn,
            )
            # ゴール不可
            if path_list is None:
                raise RuntimeError(
                    f"No path found for drone {drone_id}."
                    )
            # 探した経路を予約する
            if not reservations.reserve_path(
                path_list,
                drone_id,
            ):
                raise RuntimeError(
                    f"Failed to reserve path for drone {drone_id}."
                    )
            # 成功した経路を保存する
            planned_paths[drone_id] = path_list
        return planned_paths

