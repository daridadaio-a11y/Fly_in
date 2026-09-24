import re
import sys

from errors import MapParseError
from models import Connection, MapData, Zone


class Parser:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.total_drones = 0
        self.zones = {}
        self.connections = {}
        self._drone_count_seen = False

    def parse(self) -> MapData:
        self.total_drones = 0
        self.zones = {}
        self.connections = {}
        self._drone_count_seen = False

        with open(self.file_path, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, start=1):
                self._parse_line(line, line_num)

        self._validate()
        return MapData(
            total_drones=self.total_drones,
            zones=self.zones,
            connections=self.connections,
        )

    def _parse_line(self, line: str, line_num: int) -> None:
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#"):
            return

        content, metadata_text = self._split_metadata(clean_line, line_num)
        parts = content.split()
        prefix = parts[0]

        if prefix == "nb_drones:":
            if metadata_text:
                raise MapParseError(line_num, "nb_drones cannot have metadata.")
            self._parse_drone_count(parts, line_num)
        elif prefix in ("hub:", "start_hub:", "end_hub:"):
            self._parse_zone(parts, metadata_text, line_num)
        elif prefix == "connection:":
            self._parse_connection(parts, metadata_text, line_num)
        else:
            raise MapParseError(line_num, f"Unknown directive '{prefix}'.")

    def _split_metadata(self, line: str, line_num: int) -> tuple[str, str]:
        if "[" not in line and "]" not in line:
            return line, ""
        if line.count("[") != 1 or line.count("]") != 1:
            raise MapParseError(line_num, "Malformed metadata brackets.")

        opening = line.index("[")
        closing = line.index("]")
        if closing < opening or line[closing + 1:].strip():
            raise MapParseError(line_num, "Malformed metadata brackets.")

        content = line[:opening].strip()
        metadata_text = line[opening + 1:closing].strip()
        return content, metadata_text


    def _parse_drone_count(self, parts: list[str], line_num: int) -> None:
        if self._drone_count_seen:
            raise MapParseError(line_num, "nb_drones is defined more than once.")
        if len(parts) != 2:
            raise MapParseError(line_num, "Expected 'nb_drones: <number>'.")

        try:
            total_drones = int(parts[1])
        except ValueError as error:
            raise MapParseError(
                line_num, "The drone count must be an integer."
            ) from error
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
        if len(parts) != 4:
            raise MapParseError(
                line_num, "Expected '<hub type> <name> <x> <y>'."
            )

        role, name = parts[0], parts[1]
        if not re.fullmatch(r"[A-Za-z0-9_]+", name):
            raise MapParseError(
                line_num,
                f"Invalid zone name '{name}'. Use letters, numbers, or underscores.",
            )
        if name in self.zones:
            raise MapParseError(line_num, f"The zone name '{name}' is a duplicate.")

        try:
            x, y = int(parts[2]), int(parts[3])
        except ValueError as error:
            raise MapParseError(
                line_num, "Zone coordinates must be integers."
            ) from error

        default_capacity = float("inf") if role != "hub:" else 1
        metadata = self._parse_metadata(
            metadata_text,
            {"zone": "normal", "color": "none", "max_drones": default_capacity},
            line_num,
        )
        if metadata["zone"] not in {"normal", "restricted", "priority", "blocked"}:
            raise MapParseError(
                line_num, f"Invalid zone type '{metadata['zone']}'."
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
        if len(parts) != 2:
            raise MapParseError(
                line_num, "Expected 'connection: <zone1>-<zone2>'."
            )

        endpoints = parts[1].split("-")
        if len(endpoints) != 2 or not all(endpoints):
            raise MapParseError(line_num, "A connection needs exactly two zones.")
        zone1, zone2 = endpoints
        if zone1 == zone2:
            raise MapParseError(line_num, "A zone cannot connect to itself.")
        if zone1 not in self.zones:
            raise MapParseError(line_num, f"Zone '{zone1}' is not defined.")
        if zone2 not in self.zones:
            raise MapParseError(line_num, f"Zone '{zone2}' is not defined.")

        connection_key = tuple(sorted((zone1, zone2)))
        if connection_key in self.connections:
            raise MapParseError(
                line_num, f"The connection '{zone1} - {zone2}' is a duplicate."
            )

        metadata = self._parse_metadata(
            metadata_text, {"max_link_capacity": 1}, line_num
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
    ) -> dict:
        metadata = defaults.copy()
        if not metadata_text:
            return metadata

        seen_keys = set()
        for item in metadata_text.split():
            if item.count("=") != 1:
                raise MapParseError(line_num, f"Invalid metadata item '{item}'.")
            key, value = item.split("=", maxsplit=1)
            if key not in defaults:
                raise MapParseError(line_num, f"Unknown metadata key '{key}'.")
            if key in seen_keys:
                raise MapParseError(line_num, f"Metadata key '{key}' is duplicated.")
            seen_keys.add(key)

            if key in ("max_drones", "max_link_capacity"):
                try:
                    value = int(value)
                except ValueError as error:
                    raise MapParseError(
                        line_num, f"Metadata '{key}' must be an integer."
                    ) from error
                if value < 1:
                    raise MapParseError(
                        line_num, f"Metadata '{key}' must be positive."
                    )
            elif not value:
                raise MapParseError(line_num, f"Metadata '{key}' cannot be empty.")
            metadata[key] = value

        return metadata

    def _validate(self) -> None:
        if not self._drone_count_seen:
            raise MapParseError(0, "nb_drones is missing.")

        start_count = sum(
            zone.role == "start_hub:" for zone in self.zones.values()
        )
        end_count = sum(zone.role == "end_hub:" for zone in self.zones.values())
        if start_count != 1:
            raise MapParseError(
                0, f"Expected exactly one start_hub, found {start_count}."
            )
        if end_count != 1:
            raise MapParseError(
                0, f"Expected exactly one end_hub, found {end_count}."
            )


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <mapfile>", file=sys.stderr)
        return

    try:
        map_data = Parser(sys.argv[1]).parse()
    except (OSError, MapParseError) as error:
        print(error, file=sys.stderr)
        return

    print(map_data)


if __name__ == "__main__":
    main()
