from graph import Graph
from reservation_table import ReservationTable
from models import DroneId, ZoneName

class PathPlanner:
    """毎ターン動けるドローンを探して決める。
       ドローンの現在位置を管理
       毎ターン、移動候補を探す
       どの機体を動かせるか決める
       """
    def __init__(self, graph: Graph,
                 reservation_table: ReservationTable,
                 total_drones: int,
                 )-> None:
        self.graph = graph
        self.reservations = reservation_table
        self.total_drones = total_drones

        self.current_turn = 0
        start_name = self.graph.get_start_zone().name
        # 各ドローンの現在位置を辞書で管理
        self.drone_positions: dict[DroneId, ZoneName] = {}
        for drone_id in range(1, self.total_drones + 1):
            self.drone_positions[drone_id] = start_name

    def run(self) -> None:
        """全機がgoalに着くまでターンを繰り返す
        current_turnを一増やす
        """
        goal_name = self.graph.get_end_zone().name
        # 全機がgoalへ着くまで繰り返す
        while self.drone_positions.values() != goal_name:
            # 1ターン分の移動を決める
            self.plan_turn()
            # ターンを1進める
            self.current_turn += 1
        

    def plan_turn(self) -> None:
        """現在の一ターンで各機体の動きを決める
           移動候補を探す
           移動を決める
           移動を反映する
        """
        # ドローンごとの移動候補
        move_candidates_by_drone: dict[DroneId, list[ZoneName]] = {}
        for drone_id in self.drone_positions.keys():
            move_candidates = self.find_move_candidates(drone_id)
            move_candidates_by_drone[drone_id] = move_candidates
        chosen_moves = self.choose_moves(move_candidates_by_drone)


    def find_move_candidates(self, drone_id: int) -> list[ZoneName]:
        """各ドローンが移動できる候補を探す
           """
        move_candidates: list[ZoneName] = []
        current_zone = self.drone_positions[drone_id]
        neighbors = self.graph.get_neighbors(current_zone)
        for neighbor in neighbors:
            neighbor_zone = neighbor.name
            # 移動コストを取得
            movement_cost = self.graph.get_movement_cost(neighbor_zone)
            # 接続上のターン 
            connection_turn = self.current_turn + 1
            # ゾーンに到着するときのターン
            arrival_turn = self.current_turn + movement_cost
            if self.reservations.can_use_zone(neighbor_zone, arrival_turn) and self.reservations.can_use_connection(current_zone, neighbor_zone, connection_turn):
                    move_candidates.append(neighbor_zone)
        return move_candidates

    def choose_moves(self, move_candidates_by_drone: dict[DroneId, list[ZoneName]]) -> dict[DroneId, ZoneName]:
        """ドローンごとの全移動候補で実際に行ける移動先を探す。
           ドローンごとに実際に選んだ移動先を返す。
           """
        pass

    def apply_moves(self) -> None:
        """予約と現在位置を更新する"""
        pass