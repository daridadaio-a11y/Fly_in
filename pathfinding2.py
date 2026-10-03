"""1機のドローンについて最短経路を探索する学習用モジュール。"""

import heapq

from graph import Graph


def find_shortest_path(graph: Graph) -> list[str] | None:
    """開始ゾーンから終了ゾーンまでの最良経路を探索する。

    移動コストの合計が最小になる経路を優先し、合計コストが同じ場合は
    priorityゾーンをより多く通る経路を優先する。blockedゾーンは
    ``Graph.get_neighbors``によって探索対象から除外される。

    Args:
        graph: ゾーン、接続、移動コストを保持するグラフ。

    Returns:
        開始ゾーンから終了ゾーンまでのゾーン名を順番に格納したリスト。
        終了ゾーンへ到達できない場合はNone。
    """
    # 開始ゾーン名と終了ゾーン名を取得する。
    start_name = graph.get_start_zone().name
    end_name = graph.get_end_zone().name
    # 各ゾーンまでに見つかった最良評価を記録する辞書を作る。
    # 評価値は「合計ターン数」と「priorityの評価」を組み合わせる。
    best_scores: dict[str, tuple[int, int]] = {start_name: (0, 0)}

    # 経路復元のため、各ゾーンへどのゾーンから来たか記録する。
    previous_zone: dict[str, str | None] = {start_name: None}
    # 最初の探索候補として開始ゾーンを優先度付きキューに入れる。
    search_queue: list[tuple[int, int, str]] = [(0, 0, start_name)]
    # 探索候補が残っている間、以下の処理を繰り返す。
    #   1. キューから最も評価の良い候補を取り出す。
    #   2. すでにより良い経路が見つかっている古い候補なら無視する。
    #   3. 終了ゾーンへ到達したら探索を終了する。
    #   4. 現在ゾーンに隣接する、進入可能なゾーンを順番に調べる。
    #   5. 隣接ゾーンまでの合計ターン数を計算する。
    #   6. 隣接ゾーンがpriorityならpriority評価を更新する。
    #   7. 新しい評価が既知の評価より良ければ記録を更新する。
    #   8. 更新した隣接ゾーンを次の探索候補としてキューへ入れる。
    while search_queue:
        current_turns, priority, current_name = heapq.heappop(search_queue)
        current_score = (current_turns, priority)
        if current_score > best_scores[current_name]:
            continue
        if current_name == end_name:
            break
        for neighbor in graph.get_neighbors(current_name):
            neighbor_name = neighbor.name
            metadata = neighbor.metadata["zone"]
            movement = graph.get_movement_cost(neighbor_name)
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
    return shortest_path
