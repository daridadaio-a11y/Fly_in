
class MapParseError(Exception):
    def __init__(self, line_num, reason) -> None:
        super().__init__(f"Line {line_num}: {reason}")