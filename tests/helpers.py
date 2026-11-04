"""テスト用マップを一時ファイルから読み込む補助処理。"""

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator
from contextlib import contextmanager

from graph import Graph
from read_map import Parser


@contextmanager
def graph_from_text(map_text: str) -> Iterator[Graph]:
    """文字列のマップからGraphを作り、テスト終了後に削除する。"""
    with TemporaryDirectory() as directory:
        map_path = Path(directory) / "map.txt"
        map_path.write_text(map_text, encoding="utf-8")
        yield Graph(Parser(str(map_path)).parse())
