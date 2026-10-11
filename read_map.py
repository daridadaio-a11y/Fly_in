"""Fly-inのマップファイルを読み込み、MapDataへ変換するためのパーサー。

全体の処理は、ファイルを1行ずつ読み込み、ドローン数、ゾーン、接続、
メタデータを解析した後、マップ全体の整合性を検証する流れを想定している。
"""

from models import Zone, Connection, MapData
from errors import MapParseError


class Parser:
    """1つのマップファイルを解析し、MapDataを組み立てるクラス。

    解析中のドローン数、ゾーン、接続などをインスタンス内に保持し、
    最後にそれらをまとめたMapDataを返す役割を持つ。
    """

    def __init__(self, file_path: str) -> None:
        """解析対象となるマップファイルを設定する。

        Args:
            file_path: 読み込むマップファイルのパス。
        """
        self.file_path = file_path

    def parse(self) -> MapData:
        """マップファイル全体を解析してMapDataを返す。

        ファイルを先頭から1行ずつ読み、各行を``_parse_line``へ渡す。
        全行の解析後に``_validate``でマップ全体を検証し、ドローン数、
        ゾーン一覧、接続一覧を格納したMapDataを生成する。

        Returns:
            解析済みのマップ情報。

        Raises:
              OSError: ファイルを開けない、または読み込めない場合。
              MapParseError: マップの書式や内容が不正な場合。
        """
        self.total_drones = 0
        self.zones: dict[str, Zone] = {}
        self.connections: dict[tuple[str, str], Connection] = {}
        self._drone_count_seen = False
        self._start_hub = False
        self._end_hub = False
        line_num = 0
        with open(self.file_path, "r", encoding="utf-8") as file:
            for line in file:
                line_num += 1
                self._parse_line(line, line_num)
            self._validate()
            return MapData(total_drones=self.total_drones,
                           zones=self.zones,
                           connections=self.connections)

    def _parse_line(self, line: str, line_num: int) -> None:
        """マップファイルの1行を判別し、対応する解析処理へ振り分ける。

        空行とコメント行を無視し、先頭のキーワードに応じてドローン数、
        ゾーン、接続のいずれかとして解析する。角括弧内のメタデータは、
        本体部分から分離して各解析関数へ渡す。

        Args:
            line: ファイルから読み込んだ1行。
            line_num: エラー表示に使用する行番号。
        """
        clean_line = line.strip()
        if ("#") in clean_line:
            line_list = clean_line.split("#", maxsplit=1)
            clean_line = line_list[0].strip()
        if not clean_line:
            return
            
        content, metadata_text = self._split_metadata(clean_line, line_num)
        parts = content.split()
        if not parts:
            raise MapParseError(
                line_num,
                "Expected a directive before metadata."
                )
        prefix = parts[0]
        if not self._drone_count_seen and prefix != "nb_drones:":
            raise MapParseError(
                line_num,
                "The first non-comment line must define nb_drones."
                )
        if prefix == "nb_drones:":
            if metadata_text:
                raise MapParseError(line_num, "nb_drones cannot have metadata.")
            self._parse_drone_count(parts, line_num)
        elif prefix in ("start_hub:", "end_hub:", "hub:"):
            self._parse_zone(parts, metadata_text, line_num)
        elif prefix == "connection:":
            self._parse_connection(parts, metadata_text, line_num)
        else:
            raise MapParseError(line_num, f"Unknown directive '{prefix}'.")

    def _split_metadata(self, line: str, line_num: int) -> tuple[str, str]:
        """1行を本体部分と角括弧内のメタデータ部分に分割する。

        例えば``hub: room 1 2 [color=blue]``を、
        ``hub: room 1 2``と``color=blue``に分けることを想定している。

        Args:
            line: 分割対象の行。
            line_num: 括弧の不整合を報告するための行番号。

        Returns:
            本体部分とメタデータ文字列のタプル。メタデータがなければ、
            2番目の要素は空文字列になる。
        """
        if "[" not in line and "]" not in line:
            return line, ""
        if line.count("[") != 1 or line.count("]") != 1:
            raise MapParseError(line_num, "Malformed metadata brackets.")
        if not line.endswith("]"):
            raise MapParseError(line_num, "Nothing can appear after metadata.")
        content, metadata = line.split("[")
        metadata = metadata.rstrip("]").strip()
        if not metadata:
            raise MapParseError(line_num, "Metadata block cannot be empty.")
        return content.strip(), metadata

    def _parse_drone_count(self, parts: list[str], line_num: int) -> None:
        """``nb_drones:``行からドローン数を読み取る。

        値が整数か、1以上か、複数回定義されていないかを確認し、
        解析中のドローン総数として保存することを想定している。

        Args:
            parts: 空白で分割した行の各要素。
            line_num: エラー表示に使用する行番号。
        """
        if self._drone_count_seen:
            raise MapParseError(
                line_num,
                "nb_drones is defined more than once."
                )
        if len(parts) != 2:
            raise MapParseError(line_num, "Expected 'nb_drones: <number>'.")
        try:
            total_drones = int(parts[1])
        except ValueError as e:
            raise MapParseError(
                line_num,
                "The drone count must be an integer."
                ) from e
        if total_drones < 1:
            raise MapParseError(line_num, "The drone count must be positive.")
        self.total_drones = total_drones
        self._drone_count_seen = True
    
    def _parse_zone(
        self,
        parts: list[str],
        metadata_text: str,
        line_num: int,
    ) -> None:
        """hub、start_hub、end_hubの定義からZoneを生成する。

        ゾーン名、X・Y座標、役割、メタデータを解析し、名前の重複や
        値の妥当性を確認したうえでゾーン一覧へ追加する。

        Args:
            parts: メタデータを除いたゾーン定義の各要素。
            metadata_text: 角括弧内に書かれたメタデータ文字列。
            line_num: エラー表示に使用する行番号。
        """
        if len(parts) != 4:
            raise MapParseError(line_num, "Expected '<hub type> <name> <x> <y>'.")
        role, name = parts[0], parts[1]
        if "-" in name:
            raise MapParseError(
                line_num,
                f"The zone name '{name}' cannot contain '-'."
                )
        if name in self.zones:
            raise MapParseError(
                line_num,
                f"The zone name '{name}' is already defined."
                )
        try:
            x, y = int(parts[2]), int(parts[3])
        except ValueError as e:
            raise MapParseError(
                line_num,
                "Zone coordinates must be integers."
                ) from e
        if role == "start_hub:" or role == "end_hub:":
            if role == "start_hub:":
                if self._start_hub:
                    raise MapParseError(
                        line_num,
                        f"{role.removesuffix(':')} is defined more than once."
                        )
                self._start_hub = True
            elif role == "end_hub:":
                if self._end_hub:
                    raise MapParseError(
                        line_num,
                        f"{role.removesuffix(':')} is defined more than once."
                        )
                self._end_hub = True
            metadata = self._parse_metadata(
                metadata_text,
                {"zone": "normal", "color": "none"},
                line_num,
                ignored_key="max_drones",
            )
        else:
            metadata = self._parse_metadata(
                metadata_text,
                {"zone": "normal", "color": "none", "max_drones": 1},
                line_num,
            )
        if metadata["zone"] not in (
                "normal", "blocked", "restricted", "priority"):
            raise MapParseError(
                line_num,
                f"Invalid zone type '{metadata['zone']}'."
                )

        self.zones[name] = Zone(
            name=name,
            role=role,
            metadata=metadata,
            x=x,
            y=y,
        )

    def _parse_connection(
        self,
        parts: list[str],
        metadata_text: str,
        line_num: int,
    ) -> None:
        """``connection:``行から2つのゾーン間の接続を生成する。

        接続元と接続先が定義済みか、同じゾーン同士ではないか、
        同じ接続が既に登録されていないかを確認する。接続容量などの
        メタデータも解析し、Connectionとして接続一覧へ追加する。

        Args:
            parts: メタデータを除いた接続定義の各要素。
            metadata_text: 角括弧内に書かれたメタデータ文字列。
            line_num: エラー表示に使用する行番号。
        """
        if len(parts) != 2:
            raise MapParseError(
                line_num,
                "Expected 'connection: <zone1>-<zone2>'."
                )
        endpoints = parts[1].split("-")
        if len(endpoints) != 2 or not all(endpoints):
            raise MapParseError(
                line_num,
                "A connection needs exactly two zones."
                )
        zone1, zone2 = endpoints
        if zone1 == zone2:
            raise MapParseError(line_num, "A zone cannot connect to itself.")
        if zone1 not in self.zones:
            raise MapParseError(line_num, f"Zone '{zone1}' is not defined.")
        if zone2 not in self.zones:
            raise MapParseError(line_num, f"Zone '{zone2}' is not defined.")

        if zone1 < zone2:
            connection_key = (zone1, zone2)
        else:
            connection_key = (zone2, zone1)
        if connection_key in self.connections:
            raise MapParseError(
                line_num,
                f"The connection '{zone1} - {zone2}' is a duplicate.")
        metadata = self._parse_metadata(
            metadata_text,
            {"max_link_capacity": 1},
            line_num,
        )
        self.connections[connection_key] = Connection(
            zone1=zone1,
            zone2=zone2,
            metadata=metadata,
        )

    def _parse_metadata(
        self,
        metadata_text: str,
        defaults: dict,
        line_num: int,
        ignored_key: str | None = None
    ) -> dict:
        """``key=value``形式のメタデータを辞書へ変換する。

        省略された項目には``defaults``の値を使用する。容量を表す項目は
        整数へ変換し、未知のキー、重複したキー、不正な値なども検査する。

        Args:
            metadata_text: 空白区切りのメタデータ文字列。
            defaults: 許可するキーと、そのデフォルト値を持つ辞書。
            line_num: エラー表示に使用する行番号。

        Returns:
            デフォルト値とファイル内の指定を統合したメタデータ辞書。
        """
        metadata = defaults.copy()
        seen_keys = set()
        if not metadata_text:
            return metadata
        for item in metadata_text.split():
            if item.count("=") != 1:
                raise MapParseError(
                    line_num,
                    f"Invalid metadata item '{item}'."
                    )
            key, value = item.split("=", maxsplit=1)
            if key == ignored_key:
                continue
            if value == "":
                raise MapParseError(
                    line_num,
                    f"Metadata '{key}' must have a value."
                    )
            if key not in defaults:
                raise MapParseError(line_num, f"Unknown metadata key '{key}'.")
            if key in seen_keys:
                raise MapParseError(
                    line_num,
                    f"Metadata key '{key}' is duplicated."
                    )
            seen_keys.add(key)

            if key in ("max_drones", "max_link_capacity"):
                try:
                    number = int(value)
                except ValueError as e:
                    raise MapParseError(
                        line_num,
                        f"Metadata '{key}' must be an integer."
                        ) from e
                if number < 1:
                    raise MapParseError(
                        line_num,
                        f"Metadata '{key}' must be positive.",
                    )
                metadata[key] = number
            else:
                metadata[key] = value
        return metadata

    def _validate(self) -> None:
        """全行の解析後に、マップ全体の必須条件を検証する。

        ドローン数が定義されていること、start_hubとend_hubがそれぞれ
        ちょうど1つ存在することなど、単独の行だけでは判断できない条件を
        確認することを想定している。
        """
        if not self._drone_count_seen:
            raise MapParseError(None, "nb_drones is missing.")
        elif not self._start_hub:
            raise MapParseError(None, "Exactly one start_hub is required.")
        elif not self._end_hub:
            raise MapParseError(None, "Exactly one end_hub is required.")
