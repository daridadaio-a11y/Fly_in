
class MapParseError(Exception):
    def __init__(self, line_num: int | None, reason: str) -> None:
        if line_num is None:
            message = reason
        else:
            message = (f"Line {line_num}: {reason}")
        super().__init__(message)