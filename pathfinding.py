"""グラフ上でドローンの経路を探索するモジュール。"""

import heapq
from graph import Graph
from models import ZoneName


class PathFinder:
    """Graphを利用して開始ゾーンから終了ゾーンまでの経路を探索する。"""

    def __init__(self, graph: Graph) -> None:
        """探索対象のグラフを保存する。

        Args:
            graph: ゾーン、接続、移動コストを保持するグラフ。
        """
        self.graph = graph

    def find_shortest_path(
                           self,
                           start_name: ZoneName,
                           end_name: ZoneName
                           ) -> tuple[
                                      list[ZoneName], # 最短経路
                                      tuple[int,  int], # 合計コスト、priority評価
                                     ] | None:
        """行ける候補のゾーンからゴールのゾーンまでの最良経路を探索する。

        移動コストの合計が最小になる経路を優先し、合計コストが同じ場合は
        priorityゾーンをより多く通る経路を優先する。blockedゾーンは
        Graph.get_neighborsによって探索対象から除外される。

        Returns:
            候補のゾーンからからゴールまでの最短経路のゾーン名を順番に格納したリスト
            合計コスト、priority評価のタプル

            終了ゾーンへ到達できない場合はNone。
        """
        # tupleの辞書順比較により、ターン数が同じならpriorityを優先する。
        # ゾーン名：(ターン数、priority)
        best_scores: dict[str, tuple[int, int]] = {start_name: (0, 0)}

        # 直前のゾーンをバリューに記録し、探索終了後に経路を復元する。
        previous_zone: dict[str, str | None] = {start_name: None}
        # 現在のターン数、priority、現在のゾーン名
        search_queue: list[tuple[int, int, str]] = [(0, 0, start_name)]

        # 評価が最も良い候補から順に、隣接ゾーンを調べる。
        while search_queue:
            current_turns, priority, current_name = heapq.heappop(search_queue)
            current_score = (current_turns, priority)
            if current_score > best_scores[current_name]:
                continue
            if current_name == end_name:
                break
            for neighbor in self.graph.get_neighbors(current_name):
                neighbor_name = neighbor.name
                metadata = neighbor.metadata["zone"]
                movement = self.graph.get_movement_cost(neighbor_name)
                candidate_turns = current_turns + movement
                candidate_priority = priority

                if metadata == "priority":
                    candidate_priority -= 1
                candidate_score = (candidate_turns, candidate_priority)
                known_score = best_scores.get(neighbor_name)

                if known_score is None or candidate_score < known_score:
                    best_scores[neighbor_name] = candidate_score
                    previous_zone[neighbor_name] = current_name
                    heapq.heappush(
                        search_queue,
                        (candidate_turns, candidate_priority, neighbor_name),
                    )

        # 終了ゾーンが見つからなければNoneを返す。
        if end_name not in best_scores:
            return None

        # 終了ゾーンからprevious情報を逆向きにたどって経路を作る。
        shortest_path: list[str] = []
        path_zone_name: str | None = end_name
        while path_zone_name is not None:
            shortest_path.append(path_zone_name)
            path_zone_name = previous_zone[path_zone_name]

        # 経路を開始ゾーンからの順番に直して返す。
        shortest_path.reverse()
        return shortest_path, best_scores[end_name] #
