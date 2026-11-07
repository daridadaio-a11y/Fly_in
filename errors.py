
class MapParseError(Exception):
    """マップ入力の行番号とエラー理由を表す例外。"""

    def __init__(self, line_num: int | None, reason: str) -> None:
        """行番号がある場合は、理由と合わせてエラー文を作る。"""
        if line_num is None:
            message = reason
        else:
            message = (f"Line {line_num}: {reason}")
        super().__init__(message)
