"""Parserの正常入力と代表的な異常入力を確認する。"""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from errors import MapParseError
from read_map import Parser


class ParserTests(unittest.TestCase):
    """マップ形式とエラー処理を確認する。"""

    def _parse(self, map_text: str):
        with TemporaryDirectory() as directory:
            map_path = Path(directory) / "map.txt"
            map_path.write_text(map_text, encoding="utf-8")
            return Parser(str(map_path)).parse()

    def test_defaults_and_comments(self) -> None:
        map_data = self._parse(
            """
            # comment
            nb_drones: 2
            start_hub: start 0 0
            hub: middle 1 0
            end_hub: goal 2 0
            connection: start-middle
            connection: middle-goal
            """
        )

        self.assertEqual(map_data.total_drones, 2)
        self.assertEqual(map_data.zones["middle"].metadata["zone"], "normal")
        self.assertEqual(map_data.zones["middle"].metadata["max_drones"], 1)
        connection = map_data.connections[("middle", "start")]
        self.assertEqual(connection.metadata["max_link_capacity"], 1)

    def test_rejects_invalid_maps(self) -> None:
        invalid_maps = {
            "missing drone count": """
                start_hub: start 0 0
                end_hub: goal 1 0
            """,
            "invalid zone type": """
                nb_drones: 1
                start_hub: start 0 0
                hub: bad 1 0 [zone=unknown]
                end_hub: goal 2 0
            """,
            "missing start": """
                nb_drones: 1
                end_hub: goal 1 0
            """,
            "zero capacity": """
                nb_drones: 1
                start_hub: start 0 0
                hub: middle 1 0 [max_drones=0]
                end_hub: goal 2 0
            """,
            "duplicate zone": """
                nb_drones: 1
                start_hub: start 0 0
                end_hub: goal 1 0
                hub: goal 2 0
            """,
            "reverse duplicate connection": """
                nb_drones: 1
                start_hub: start 0 0
                end_hub: goal 1 0
                connection: start-goal
                connection: goal-start
            """,
            "undefined endpoint": """
                nb_drones: 1
                start_hub: start 0 0
                end_hub: goal 1 0
                connection: start-missing
            """,
        }

        for name, map_text in invalid_maps.items():
            with self.subTest(name=name):
                with self.assertRaises(MapParseError):
                    self._parse(map_text)


if __name__ == "__main__":
    unittest.main()
