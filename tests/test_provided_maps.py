"""提供マップの完走、容量、移動コスト、参考ターン数を確認する。"""

from collections import Counter
from pathlib import Path
import unittest

from graph import Graph
from models import DroneId, ZoneAtTurn
from path_planner import PathPlanner
from read_map import Parser
from simulation import Simulation


ROOT = Path(__file__).resolve().parents[1]

BENCHMARKS = {
    "maps/easy/01_linear_path.txt": 6,
    "maps/easy/02_simple_fork.txt": 8,
    "maps/easy/03_basic_capacity.txt": 6,
    "maps/medium/01_dead_end_trap.txt": 12,
    "maps/medium/02_circular_loop.txt": 14,
    "maps/medium/03_priority_puzzle.txt": 12,
    "maps/hard/01_maze_nightmare.txt": 30,
    "maps/hard/02_capacity_hell.txt": 35,
    "maps/hard/03_ultimate_challenge.txt": 45,
    "maps/challenger/01_the_impossible_dream.txt": 44,
}


class ProvidedMapTests(unittest.TestCase):
    """提供された到達可能マップをすべて計画して検証する。"""

    def _validate_paths(
        self,
        graph: Graph,
        paths: dict[DroneId, list[ZoneAtTurn]],
    ) -> None:
        zone_usage: Counter[tuple[str, int]] = Counter()
        connection_usage: Counter[tuple[str, str, int]] = Counter()
        start_name = graph.get_start_zone().name
        goal_name = graph.get_end_zone().name

        for path in paths.values():
            self.assertEqual(path[0], (start_name, 0))
            self.assertEqual(path[-1][0], goal_name)

            for zone_name, turn in path[1:]:
                zone = graph.zones[zone_name]
                self.assertNotEqual(zone.metadata["zone"], "blocked")
                if zone.role not in ("start_hub:", "end_hub:"):
                    zone_usage[(zone_name, turn)] += 1

            for previous, current in zip(path, path[1:]):
                previous_zone, previous_turn = previous
                current_zone, current_turn = current
                if previous_zone == current_zone:
                    self.assertEqual(current_turn - previous_turn, 1)
                    continue

                connection = graph.get_connection(previous_zone, current_zone)
                self.assertIsNotNone(connection)
                self.assertEqual(
                    current_turn - previous_turn,
                    graph.get_movement_cost(current_zone),
                )
                assert connection is not None
                connection_usage[
                    (connection.zone1, connection.zone2, previous_turn + 1)
                ] += 1

        for (zone_name, _turn), count in zone_usage.items():
            capacity = graph.zones[zone_name].metadata["max_drones"]
            assert isinstance(capacity, int)
            self.assertLessEqual(count, capacity)

        for (zone1, zone2, _turn), count in connection_usage.items():
            connection = graph.get_connection(zone1, zone2)
            assert connection is not None
            capacity = connection.metadata["max_link_capacity"]
            assert isinstance(capacity, int)
            self.assertLessEqual(count, capacity)

    def test_reachable_maps_are_valid_and_meet_benchmarks(self) -> None:
        for relative_path, maximum_turns in BENCHMARKS.items():
            with self.subTest(map=relative_path):
                map_data = Parser(str(ROOT / relative_path)).parse()
                graph = Graph(map_data)
                paths = PathPlanner(graph, map_data.total_drones).plan_all()
                self._validate_paths(graph, paths)

                output_lines = Simulation(graph, paths).run()
                self.assertTrue(all(output_lines))
                self.assertLessEqual(len(output_lines), maximum_turns)

    def test_unreachable_map_fails_cleanly(self) -> None:
        map_path = ROOT / "maps/tests/04_unreachable_goal.txt"
        map_data = Parser(str(map_path)).parse()
        graph = Graph(map_data)

        with self.assertRaisesRegex(RuntimeError, "No path exists"):
            PathPlanner(graph, map_data.total_drones).plan_all()


if __name__ == "__main__":
    unittest.main()
