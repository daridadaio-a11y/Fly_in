"""複数ドローンをターン単位で移動させるシミュレーション。"""

from graph import Graph


class Simulation:
    """複数のドローンを1本の共通経路に沿って移動させる。"""

    def __init__(
        self,
        graph: Graph,
        path: list[str],
        total_drones: int,
    ) -> None:
        """グラフと経路を保存し、全ドローンをstartへ配置する。"""
        self.graph = graph
        self.path = path
        self.total_drones = total_drones
        self._validate_inputs()
        self.drone_positions = {
            drone_id: 0 for drone_id in range(1, total_drones + 1)
        }
        self.delivered_drones: set[int] = set()
        self.turn = 0
        self.history: list[list[str]] = []

    def _validate_inputs(self) -> None:
        """経路と機体数がシミュレーション可能か検査する。"""
        if self.total_drones < 1:
            raise ValueError("The number of drones must be positive.")
        if len(self.path) < 2:
            raise ValueError("The path must contain at least start and end.")
        if self.path[0] != self.graph.get_start_zone().name:
            raise ValueError("The path must begin at the start zone.")
        if self.path[-1] != self.graph.get_end_zone().name:
            raise ValueError("The path must end at the end zone.")

        for zone_name in self.path:
            if zone_name not in self.graph.zones:
                raise ValueError(f"Unknown zone in path: '{zone_name}'.")
            zone_type = self.graph.zones[zone_name].metadata["zone"]
            if zone_type == "blocked":
                raise ValueError(
                    f"The path enters blocked zone '{zone_name}'."
                )
            if zone_type == "restricted":
                raise ValueError(
                    "Restricted zones are not supported by this "
                    "simulation yet."
                )

        for source, destination in zip(self.path, self.path[1:]):
            if self.graph.get_connection(source, destination) is None:
                raise ValueError(
                    f"No connection between '{source}' and '{destination}'."
                )

    def _count_zone_occupancy(self) -> dict[str, int]:
        """現在それぞれのゾーンにいる未配達ドローン数を返す。"""
        occupancy = {name: 0 for name in self.graph.zones}
        for drone_id, path_index in self.drone_positions.items():
            if drone_id not in self.delivered_drones:
                occupancy[self.path[path_index]] += 1
        return occupancy

    def _has_capacity(
        self,
        zone_name: str,
        occupancy: dict[str, int],
    ) -> bool:
        """移動先ゾーンに1機分の空きがあるか返す。"""
        zone = self.graph.zones[zone_name]
        if zone.role in ("start_hub:", "end_hub:"):
            return True
        capacity = zone.metadata["max_drones"]
        if not isinstance(capacity, int):
            raise ValueError(f"Invalid capacity for zone '{zone_name}'.")
        return occupancy[zone_name] < capacity

    def run_turn(self) -> list[str]:
        """容量制約を守りながら1ターン進める。"""
        if len(self.delivered_drones) == self.total_drones:
            return []

        occupancy = self._count_zone_occupancy()
        connection_usage: dict[tuple[str, str], int] = {}
        movements: list[str] = []
        active = (
            drone_id for drone_id in self.drone_positions
            if drone_id not in self.delivered_drones
        )
        ordered = sorted(
            active,
            key=lambda drone_id: (-self.drone_positions[drone_id], drone_id),
        )

        # goalに近い機体から動かし、同じターンに後方の容量を空ける。
        for drone_id in ordered:
            source_index = self.drone_positions[drone_id]
            source = self.path[source_index]
            destination = self.path[source_index + 1]
            connection = self.graph.get_connection(source, destination)
            if connection is None:
                raise ValueError(
                    f"Missing connection: '{source}-{destination}'."
                )

            if source < destination:
                connection_key = (source, destination)
            else:
                connection_key = (destination, source)
            link_capacity = connection.metadata["max_link_capacity"]
            if not isinstance(link_capacity, int):
                raise ValueError(
                    f"Invalid capacity for '{source}-{destination}'."
                )
            if connection_usage.get(connection_key, 0) >= link_capacity:
                continue
            if not self._has_capacity(destination, occupancy):
                continue

            occupancy[source] -= 1
            occupancy[destination] += 1
            connection_usage[connection_key] = (
                connection_usage.get(connection_key, 0) + 1
            )
            self.drone_positions[drone_id] += 1
            movements.append(f"D{drone_id}-{destination}")
            if destination == self.path[-1]:
                self.delivered_drones.add(drone_id)

        if not movements:
            raise ValueError(
                "Simulation cannot progress; all drones are blocked."
            )
        self.turn += 1
        self.history.append(movements)
        return movements

    def run(self) -> list[list[str]]:
        """全ドローンが終了ゾーンへ到達するまで実行する。"""
        while len(self.delivered_drones) < self.total_drones:
            self.run_turn()
        return self.history


def simulate_single_path(
    graph: Graph,
    path: list[str],
    total_drones: int,
) -> list[list[str]]:
    """従来の関数形式でSimulationを実行する。"""
    return Simulation(graph, path, total_drones).run()
