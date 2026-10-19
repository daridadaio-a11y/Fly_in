"""計画済みの時間付き経路をターン単位で再生する設計骨組み。

全機分の完成経路をターン順に表示する
"""

from graph import Graph
from path_planner import PathPlanner


class Simulation:

    def __init_(self, graph: Graph, path_planner: PathPlanner) -> None:
        self.graph = graph
        self.path_planner = path_planner
        planned_path = self.path_planner.plan_all()