from read_map import Parser
from errors import MapParseError
from graph import Graph
from path_planner import PathPlanner
from simulation import Simulation
import sys


def main() -> int:
    """コマンドラインからパーサーを実行するための入口。

    コマンドライン引数からマップファイルのパスを受け取り、Parserで
    解析する。成功時には解析結果を表示し、失敗時には利用方法または
    エラーメッセージを標準エラー出力へ表示することを想定している。
    """
    visual_mode = False

    if len(sys.argv) == 2:
        file_path = sys.argv[1]
    elif len(sys.argv) == 3 and sys.argv[1] == "--visual":
        visual_mode = True
        file_path = sys.argv[2]
    else:
        print(
            "Usage: python3 fly_in.py [--visual] <mapfile>",
            file=sys.stderr,
        )
        return 1
    try:
        parser = Parser(file_path)
        map_data = parser.parse()
        graph = Graph(map_data)
        total_drones = map_data.total_drones
        path_planner = PathPlanner(graph, total_drones)
        planned_paths = path_planner.plan_all()
        simulation = Simulation(graph, planned_paths)

        output_lines = simulation.run()
        for output_line in output_lines:
            print(output_line)

        if visual_mode:
            # 遅延インポート
            from visualizer import Visualizer

            visualizer = Visualizer(graph)
            visualizer.make_pygame()

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
