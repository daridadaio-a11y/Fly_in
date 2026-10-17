"""計画済みの時間付き経路をターン単位で再生する設計骨組み。

全機分の完成経路をターン順に表示する
"""

from graph import Graph


class Simulation:
    """全機の時間付き経路をターン順の移動へ変換する。

    管理する予定の状態:
        graph: ゾーン種別、色、接続名を参照するGraph。
        planned_paths: 機体IDごとに決定済みの時間付き経路。
        current_turn: 現在再生中のターン。
        final_turn: 最も遅い機体がgoalへ到着するターン。
        history: ターンごとの出力文字列。
    """

    def __init__(
        self,
        graph: Graph,
        planned_paths: dict[int, list[tuple[str, int]]],
    ) -> None:
        """計画済み経路を検証し、再生開始前の状態を用意する。"""

    def _validate_planned_paths(self) -> None:
        """全経路がstartから始まり、goalへ到着することを確認する。

        機体IDが重複していないこと、ターンが昇順であること、連続する
        状態が待機またはGraph上の有効な移動であることも検証する。
        """

    def _movement_at_turn(
        self,
        drone_id: int,
        turn: int,
    ) -> str | None:
        """指定機体がそのターンに出力する移動文字列を返す。

        normal/priorityへの到着は``D<ID>-<zone>``、restrictedへ向かう
        接続上では``D<ID>-<connection>``とする。待機中とgoal到着後は
        出力しない。
        """

    def run_turn(self) -> list[str]:
        """現在ターンに発生する全機の移動をID順に返す。

        全機について``_movement_at_turn``を確認し、None以外だけを
        そのターンの出力へ追加する。その後current_turnを進める。
        """

    def run(self) -> list[list[str]]:
        """final_turnまで計画を再生し、ターンごとの移動履歴を返す。"""

    def format_output(self) -> list[str]:
        """各ターンの移動を空白区切りの1行へ変換する。

        Returns:
            課題指定の``D<ID>-<zone>``または``D<ID>-<connection>``を
            ターンごとにまとめた文字列のリスト。
        """

    def get_positions_at_turn(self, turn: int) -> dict[int, str]:
        """可視化のため、指定ターンの各未配達機の場所を返す。"""
