"""ReservationPathを全機分繰り返して予約する"""

from graph import Graph
from reservation_table import ReservationTable
from reservation_pathfinder import ReservationPathFinder
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
        self.reservations = ReservationTable(graph)
        self.pathfinder = ReservationPathFinder(graph)
        self.planned_paths: dict[DroneId, list[ZoneAtTurn]] = {}
            
    def plan_all(self, max_turn: int):
        """探索ｰ>reserve_pathで経路を予約ｰ>planned_pathsへ保存、を繰り返す"""
        for drone_id in range(1, self.total_drones + 1):
            pass