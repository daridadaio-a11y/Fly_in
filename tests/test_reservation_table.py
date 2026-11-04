"""ゾーン容量と双方向接続容量を確認する。"""

import unittest

from reservation_table import ReservationTable
from tests.helpers import graph_from_text


MAP_TEXT = """
nb_drones: 3
start_hub: start 0 0
hub: middle 1 0 [max_drones=1]
end_hub: goal 2 0
connection: start-middle [max_link_capacity=1]
connection: middle-goal
"""


class ReservationTableTests(unittest.TestCase):
    """同一ターンの予約が容量を超えないことを確認する。"""

    def test_zone_capacity(self) -> None:
        with graph_from_text(MAP_TEXT) as graph:
            reservations = ReservationTable(graph)
            self.assertTrue(reservations.reserve_zone("middle", 1, 1))
            self.assertFalse(reservations.can_use_zone("middle", 1))
            self.assertFalse(reservations.reserve_zone("middle", 1, 2))
            self.assertTrue(reservations.can_use_zone("middle", 2))

    def test_connection_capacity_is_undirected(self) -> None:
        with graph_from_text(MAP_TEXT) as graph:
            reservations = ReservationTable(graph)
            self.assertTrue(
                reservations.reserve_connection("start", "middle", 1, 1)
            )
            self.assertFalse(
                reservations.can_use_connection("middle", "start", 1)
            )
            self.assertTrue(
                reservations.can_use_connection("middle", "start", 2)
            )

    def test_start_and_goal_have_unlimited_capacity(self) -> None:
        with graph_from_text(MAP_TEXT) as graph:
            reservations = ReservationTable(graph)
            for drone_id in range(1, 4):
                self.assertTrue(
                    reservations.reserve_zone("start", 1, drone_id)
                )
                self.assertTrue(
                    reservations.reserve_zone("goal", 3, drone_id)
                )


if __name__ == "__main__":
    unittest.main()
