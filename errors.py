
class MapParseError(Exception):
    def __init__(self, line_num, reason) -> None:
        if line_num:
            super().__init__(f"Line {line_num}: {reason}")
        elif line_num is None:
            super().__init__(f"{reason}")