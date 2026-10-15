from graph import Graph
from pathfinding import PathFinder
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
           いま移動可能な隣接ゾーンを集める
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
        """ドローンごとの移動候補を評価し、実際の移動先を決める
           
           各ドローンについて
              空のcandidate_scoresを作る
              各移動候補からgoalまでの経路を探す
              移動コストとpriorityの評価tupleをcandidate_scoresへ追加する
              評価順に並べ、容量を再確認し、予約可能な最初の候補を選ぶ
              選ばれたゾーンをchosen_movesへ保存する
            ドローンごとに実際に選んだ移動先を返す
        """
        chosen_moves: dict[DroneId, ZoneName] = {}
        goal_name = self.graph.get_end_zone().name
        pathfinder = PathFinder(self.graph)
        drone_ids = move_candidates_by_drone.keys()
        # 各ドローンの各候補からgoalまでの経路を探す
        for drone_id in drone_ids:
            # 最短コスト、priority、zone_nameのtuple
            candidate_scores: list[tuple[int, int, ZoneName]] = []
            move_candidates = move_candidates_by_drone[drone_id]
            
            for candidate_zone in move_candidates:
                result = pathfinder.find_shortest_path(candidate_zone, goal_name)
                if result is None:
                    continue
                _path, score = result # 各候補の最短経路、合計移動コストpriority評価のtuple
                remaining_cost, remaining_priority = score 
                # 候補からゴールまでの移動コスト、priorityの評価
                first_move_cost = self.graph.get_movement_cost(candidate_zone)
                
                candidate = self.graph.zones[candidate_zone]
                candidate_type = candidate.metadata["zone"]

                # candidate_zoneのmetadataがpriorityかチェックする
                first_priority_score = 0
                if candidate_type == "priority":
                    first_priority_score = -1
                # 現在地から候補まで+候補からゴールまで
                total_cost = first_move_cost + remaining_cost
                total_priority_score = (
                    first_priority_score + remaining_priority
                )
                candidate_scores.append(
                    (
                        total_cost,
                        total_priority_score,
                        candidate_zone,
                    )
                )
            if not candidate_scores:
                continue
            # 候補を合計コスト、
            candidate_scores.sort()
            # 評価順に容量を再確認し、予約可能な最初の候補を選ぶ
            chosen_zone = self.choose_and_reserve_move(drone_id, candidate_scores)
            if chosen_zone is None:
                continue
            # 選択できたドローンの移動先を記録する
            chosen_moves[drone_id] = chosen_zone
            
        return chosen_moves

# D1とD2が同じAを選んだ場合、容量をこえてしまう。
# 今の時点で各ドローンが行けるゾーン,connectionがはいっているせいで先に行ったドローンのいるゾーンが容量オーバーになっていないか確かめる必要がある
"""D1を処理
    Aが最良
    Aはまだ空いている
    D1がAを予約

D2を処理
    Aが最良
    しかしD1が予約済み
    Aは使えない
    次の候補Bを確認
    Bが空いていればD2がBを予約"""
    def choose_and_reserve_move(
            self,
            drone_id: DroneId,
            candidate_scores: list[tuple[int, int, ZoneName]],
            ) -> ZoneName | None:
        """評価順に候補を確認
           ゾーンと容量を再確認
           使用可能なら予約する
           選んだゾーンを返す"""  
              各candidate_scoreについて
    candidate_zoneを取り出す
    current_zoneを取得
    connection_turnを計算
    arrival_turnを計算

    ゾーンと接続の両方が空いているか確認
        空いていれば両方を予約
        candidate_zoneを返す

全部試しても予約できなければNone
    def apply_moves(self,chosen_moves: dict[DroneId, ZoneName]) -> None:
        """予約と現在位置を更新する"""
        pass