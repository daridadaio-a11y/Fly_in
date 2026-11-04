"""計画済み経路をターンごとの状態と出力文字列へ変換する。"""

from graph import Graph
from models import DroneId, ZoneAtTurn, ZoneName, TurnState


class Simulation:
    """計画済み経路からターンごとのシミュレーション状態を作る。"""
    def __init__(self,
                 graph: Graph,
                 planned_paths: dict[DroneId, list[ZoneAtTurn]],
                 ) -> None:
        """グラフと全機の計画済み経路を保存する。"""
        self.graph = graph
        self.planned_paths = planned_paths

    def run(self) -> list[str]:
        """各ターンの移動を課題指定形式の文字列として返す。"""
        turn_states = self.build_turn_states()
        output_lines = []  # 全ターンの完成行
        for state in turn_states:
            output = " ".join(state["movements"])
            output_lines.append(output)
        return output_lines

    def build_turn_states(self) -> list[TurnState]:
        """計画済み経路から全ターンの状態を作る。"""
        # 全ドローンを見てfinal_turnを確定する
        final_turn = 0
        # 全ターンの詳しい状態を順番に保存するリスト
        turn_states: list[TurnState] = []
        for path in self.planned_paths.values():
            # 各経路の最後にあるゴール到着ターンを取得する
            goal_turn = path[-1][1]
            if goal_turn > final_turn:
                final_turn = goal_turn

        # そのターンについて全ドローンを確認
        for turn in range(1, final_turn + 1):
            turn_state = self._build_turn_state(turn)
            turn_states.append(turn_state)

        return turn_states

    def _build_turn_state(self, turn: int) -> TurnState:
        """指定ターンの位置、使用数、移動情報を作る。"""
        turn_movements: list[str] = []  # このターンの文字出力

        # 各ドローンがどこにいるか
        drone_positions: dict[DroneId, tuple[str, ...]] = {}
        # 各ゾーンを何機使っているか
        zone_usage: dict[ZoneName, int] = {}
        # 各接続を何機使っているか
        connection_usage: dict[
            tuple[ZoneName, ZoneName],
            int,
        ] = {}
        # ゴール済みの機数
        delivered_count = 0
        for drone_id, path in self.planned_paths.items():
            goal_turn = path[-1][1]

            if turn >= goal_turn:
                delivered_count += 1

            for i in range(1, len(path)):
                previous_zone, previous_turn = path[i - 1]
                current_zone, current_turn = path[i]

                # planned_pathsの各タプルは、ターン終了時の
                # 到着ゾーンとターンを表す
                if turn == current_turn:
                    # 待機でもゾーン上の位置は保持する
                    drone_positions[drone_id] = ("zone", current_zone)
                    # current_zoneが登録済みなら現在の数を取得
                    # なければ0から開始する
                    zone_usage[current_zone] = zone_usage.get(
                        current_zone, 0
                    ) + 1

                    if previous_zone != current_zone:
                        # 実際に移動した場合のみターミナル出力
                        movement = f"D{drone_id}-{current_zone}"
                        turn_movements.append(movement)
                # 待機は位置とゾーン使用数だけを記録し、移動処理は行わない
                if previous_zone == current_zone:
                    continue

                current_zone_data = self.graph.zones[current_zone]
                zone_type = current_zone_data.metadata["zone"]

                # 接続を使用するターン
                if turn == previous_turn + 1:
                    # 両方向の移動を同じ接続として数える
                    sorted_zone1, sorted_zone2 = sorted(
                        (previous_zone, current_zone)
                    )
                    connection_key = (sorted_zone1, sorted_zone2)

                    connection_usage[connection_key] = (
                        connection_usage.get(connection_key, 0) + 1
                    )

                    # restrictedゾーンへの移動では、
                    # このターンは接続上にいる
                    if zone_type == "restricted":
                        drone_positions[drone_id] = (
                            "connection",
                            previous_zone,
                            current_zone,
                        )

                        movement = (
                            f"D{drone_id}-"
                            f"{previous_zone}-{current_zone}"
                        )
                        turn_movements.append(movement)

        return {
            "turn": turn,
            "movements": turn_movements,
            "drone_positions": drone_positions,
            "zone_usage": zone_usage,
            "connection_usage": connection_usage,
            "delivered_count": delivered_count,
        }
