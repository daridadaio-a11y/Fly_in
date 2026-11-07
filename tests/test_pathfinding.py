"""提供された小規模マップで経路選択規則を確認する。"""

from pathlib import Path
import unittest

from graph import Graph
from pathfinding import PathFinder
from read_map import Parser


ROOT = Path(__file__).resolve().parents[1]


class PathFinderTests(unittest.TestCase):
    """priority、restricted、blocked、到達不能を確認する。"""

    def _find(
        self,
        relative_path: str,
    ) -> tuple[list[str], tuple[int, int]] | None:
        map_path = ROOT / relative_path
        graph = Graph(Parser(str(map_path)).parse())
        result = PathFinder(graph).find_shortest_path("start", "goal")
        return result

    def test_equal_cost_path_prefers_priority(self) -> None:
        result = self._find("maps/tests/01_equal_cost_priority.txt")
        self.assertIsNotNone(result)
        assert result is not None
        path, score = result
        self.assertEqual(path, ["start", "priority_path", "goal"])
        self.assertEqual(score[0], 2)

    def test_restricted_cost_prefers_faster_normal_path(self) -> None:
        result = self._find("maps/tests/02_restricted_cost.txt")
        self.assertIsNotNone(result)
        assert result is not None
        path, score = result
        self.assertEqual(path, ["start", "normal_path", "goal"])
        self.assertEqual(score[0], 2)

    def test_blocked_zone_is_avoided(self) -> None:
        result = self._find("maps/tests/03_blocked_avoidance.txt")
        self.assertIsNotNone(result)
        assert result is not None
        path, _score = result
        self.assertNotIn("blocked_shortcut", path)
        self.assertEqual(path, ["start", "detour1", "detour2", "goal"])

    def test_unreachable_goal_returns_none(self) -> None:
        result = self._find("maps/tests/04_unreachable_goal.txt")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
