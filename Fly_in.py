from read_map import Parser
from errors import MapParseError
from graph import Graph
from reservation_table import ReservationTable
from ゴミ.path_planner import PathPlanner
import sys

def main() -> int:
    """コマンドラインからパーサーを実行するための入口。

    コマンドライン引数からマップファイルのパスを受け取り、Parserで
    解析する。成功時には解析結果を表示し、失敗時には利用方法または
    エラーメッセージを標準エラー出力へ表示することを想定している。
    """
    if len(sys.argv) != 2:
        print("Usage: python3 Fly_in.py <mapfile>", file=sys.stderr)
        return 1
    try:
        file_path = sys.argv[1]
        parser = Parser(file_path)
        map_data = parser.parse()
        graph = Graph(map_data)
        reservation_table = ReservationTable(graph)
        total_drones = map_data.total_drones
        path_planner = PathPlanner(graph, reservation_table, total_drones)
        start = graph.get_start_zone().name
        print(f"{start}")
        print(f"{graph.get_end_zone().name}")
        print(f"{graph.get_neighbors(start)}")
        print(f"{map_data.total_drones}")
        print(f"{map_data.connections}")
        print(f"{map_data.zones}")
        print("読み込めた！！")
    except MapParseError as e:
        print(f"MapParseError: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"OSError: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
1. マップを解析する
2. Graphを作る
3. 予約表を作る
4. 時間付き経路探索器を作る
5. 全機の経路を計画する
6. 計画できなければエラーにする
7. 計画をシミュレーションする
8. 指定形式で出力する
