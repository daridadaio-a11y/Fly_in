"""グラフ上で開始ゾーンから終了ゾーンまでの最短経路を探索する。"""

from graph import Graph
import heapq

def find_shortest_path(graph: Graph) -> list[str] | None:
    """1機のドローンが最少ターンで到達できる経路を求める。

    ゾーンごとの移動コストを考慮し、開始ゾーンから終了ゾーンまでの
    最短経路をダイクストラ法で探索する。blockedゾーンは探索しない。

    Args:
        graph: ゾーン、接続、移動コストを保持するグラフ。

    Returns:
        通過するゾーン名を開始地点から順番に格納したリスト。
        ゴールへ到達できない場合はNone。
    """
    start_name = graph.get_start_zone().name
    end_name = graph.get_end_zone().name
    distances = {}
    previous = {}
    for zone_name in graph.zones:
        distances[zone_name] = float("inf")
        previous[zone_name] = None
    distances[start_name] = 0
    serch_queue = [(0, start_name)]
