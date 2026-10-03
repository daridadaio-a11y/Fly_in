"""グラフ上で開始ゾーンから終了ゾーンまでの最短経路を探索する。"""

import heapq

from graph import Graph


def find_shortest_path(graph: Graph) -> list[str] | None:
    """1機のドローンが最少ターンで到達できる経路を求める。

    ゾーンごとの移動コストを考慮し、開始ゾーンから終了ゾーンまでの
    最短経路をダイクストラ法で探索する。合計ターン数が同じ経路では、
    priorityゾーンをより多く通る経路を優先する。

    Args:
        graph: ゾーン、接続、移動コストを保持するグラフ。

    Returns:
        通過するゾーン名を開始地点から順番に格納したリスト。
        ゴールへ到達できない場合はNone。
    """
    start_name = graph.get_start_zone().name
    end_name = graph.get_end_zone().name

    # 評価値は「合計ターン数、priority評価」の順で比較する。
    # priority評価は通過数を負数にし、通過数が多いほど小さくする。
    best_scores: dict[str, tuple[int, int]] = {start_name: (0, 0)}
    previous_zones: dict[str, str | None] = {start_name: None}
    search_queue: list[tuple[int, int, str]] = [(0, 0, start_name)]

    while search_queue:
        current_turns, priority_score, current_name = heapq.heappop(
            search_queue
        )
        current_score = (current_turns, priority_score)

        # 同じゾーンについて、すでにより良い候補が見つかっていれば無視する。
        if current_score != best_scores.get(current_name):
            continue

        # キューからgoalが取り出された時点で、その経路が最良と確定する。
        if current_name == end_name:
            break

        for neighbor in graph.get_neighbors(current_name):
            neighbor_name = neighbor.name
            movement_turns = graph.get_movement_cost(neighbor_name)
            candidate_turns = current_turns + movement_turns

            candidate_priority_score = priority_score
            if neighbor.metadata["zone"] == "priority":
                candidate_priority_score -= 1

            candidate_score = (
                candidate_turns,
                candidate_priority_score,
            )
            known_score = best_scores.get(neighbor_name)

            if known_score is None or candidate_score < known_score:
                best_scores[neighbor_name] = candidate_score
                previous_zones[neighbor_name] = current_name
                heapq.heappush(
                    search_queue,
                    (
                        candidate_turns,
                        candidate_priority_score,
                        neighbor_name,
                    ),
                )

    if end_name not in best_scores:
        return None

    shortest_path: list[str] = []
    current_name: str | None = end_name
    while current_name is not None:
        shortest_path.append(current_name)
        current_name = previous_zones[current_name]

    shortest_path.reverse()
    return shortest_path
