"""Simulationの通常移動、待機、restricted出力を確認する。"""

import unittest

from simulation import Simulation
from tests.helpers import graph_from_text


MAP_TEXT = """
nb_drones: 2
start_hub: start 0 0
hub: normal 1 0
hub: restricted 2 0 [zone=restricted]
end_hub: goal 3 0
connection: start-normal
connection: normal-restricted
connection: restricted-goal
"""


class SimulationTests(unittest.TestCase):
    """計画済み経路をターン単位の文字列へ変換する処理を確認する。"""

    def test_waiting_drone_is_omitted(self) -> None:
        with graph_from_text(MAP_TEXT) as graph:
            paths = {
                1: [("start", 0), ("normal", 1), ("goal", 2)],
                2: [
                    ("start", 0),
                    ("start", 1),
                    ("normal", 2),
                    ("goal", 3),
                ],
            }
            self.assertEqual(
                Simulation(graph, paths).run(),
                [
                    "D1-normal",
                    "D1-goal D2-normal",
                    "D2-goal",
                ],
            )

    def test_restricted_move_outputs_connection_then_zone(self) -> None:
        with graph_from_text(MAP_TEXT) as graph:
            paths = {
                1: [
                    ("start", 0),
                    ("normal", 1),
                    ("restricted", 3),
                    ("goal", 4),
                ]
            }
            self.assertEqual(
                Simulation(graph, paths).run(),
                [
                    "D1-normal",
                    "D1-normal-restricted",
                    "D1-restricted",
                    "D1-goal",
                ],
            )

    def test_build_turn_states_records_detailed_state(self) -> None:
        with graph_from_text(MAP_TEXT) as graph:
            paths = {
                1: [
                    ("start", 0),
                    ("normal", 1),
                    ("restricted", 3),
                    ("goal", 4),
                ],
                2: [
                    ("start", 0),
                    ("start", 1),
                    ("normal", 2),
                    ("goal", 3),
                ],
            }

            states = Simulation(graph, paths).build_turn_states()

            self.assertEqual(
                states,
                [
                    {
                        "turn": 1,
                        "movements": ["D1-normal"],
                        "drone_positions": {
                            1: ("zone", "normal"),
                            2: ("zone", "start"),
                        },
                        "zone_usage": {"normal": 1, "start": 1},
                        "connection_usage": {("normal", "start"): 1},
                        "delivered_count": 0,
                    },
                    {
                        "turn": 2,
                        "movements": [
                            "D1-normal-restricted",
                            "D2-normal",
                        ],
                        "drone_positions": {
                            1: ("connection", "normal", "restricted"),
                            2: ("zone", "normal"),
                        },
                        "zone_usage": {"normal": 1},
                        "connection_usage": {
                            ("normal", "restricted"): 1,
                            ("normal", "start"): 1,
                        },
                        "delivered_count": 0,
                    },
                    {
                        "turn": 3,
                        "movements": ["D1-restricted", "D2-goal"],
                        "drone_positions": {
                            1: ("zone", "restricted"),
                            2: ("zone", "goal"),
                        },
                        "zone_usage": {"restricted": 1, "goal": 1},
                        "connection_usage": {("goal", "normal"): 1},
                        "delivered_count": 1,
                    },
                    {
                        "turn": 4,
                        "movements": ["D1-goal"],
                        "drone_positions": {1: ("zone", "goal")},
                        "zone_usage": {"goal": 1},
                        "connection_usage": {("goal", "restricted"): 1},
                        "delivered_count": 2,
                    },
                ],
            )

    def test_connection_usage_combines_both_directions(self) -> None:
        with graph_from_text(MAP_TEXT) as graph:
            paths = {
                1: [("normal", 0), ("restricted", 2)],
                2: [("restricted", 0), ("normal", 1)],
            }

            first_turn = Simulation(graph, paths).build_turn_states()[0]

            self.assertEqual(
                first_turn["connection_usage"],
                {("normal", "restricted"): 2},
            )


if __name__ == "__main__":
    unittest.main()
