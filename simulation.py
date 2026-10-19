"""計画済みの時間付き経路をターン単位で再生する設計骨組み。

全機分の完成経路をターン順に表示する
"""

from graph import Graph
from models import DroneId, ZoneAtTurn


class Simulation:
    """計画済みの時間付き経路をターン単位の移動へ変換する"""
    def __init__(self,
                 graph: Graph,
                 planned_paths: dict[DroneId, list[ZoneAtTurn]],
                 ) -> None:
        """グラフと全機の計画済み経路を保存する"""
        self.graph = graph
        self.planned_paths = planned_paths

    def run(self) -> list[str]:
        """ターン1で全ドローンを確認
           → ターン2で全ドローンを確認
           → ターン3で全ドローンを確認"""






"""
Simulation
├── __init__()
│   └── graphとplanned_pathsを保存する
│
├── run()
│   └── ターン1から最終ターンまで処理し、出力行のリストを返す
│
└── _movement_at_turn()
    └── 指定した1機が指定ターンに何を出力するか判定する
```

まずは、この3メソッドだけで作れます。

### 1. `__init__()`

現在実装中の部分です。

```python
def __init__(
    self,
    graph: Graph,
    planned_paths: dict[DroneId, list[ZoneAtTurn]],
) -> None:
```

保存するもの：

```python
self.graph
self.planned_paths
```

### 2. `run()`

Simulationの中心となる公開メソッドです。

```python
def run(self) -> list[str]:
```

役割は次のとおりです。

```text
最終ターンを求める
↓
ターン1から最終ターンまで繰り返す
↓
各ターンについて全ドローンを調べる
↓
そのターンに動いたドローンの文字列を集める
↓
空白でつないで1行にする
↓
全行のリストを返す
```

戻り値の例：

```python
[
    "D1-A",
    "D1-goal D2-A",
    "D2-goal",
]
```

### 3. `_movement_at_turn()`

1機・1ターンだけを判定する補助メソッドです。

```python
def _movement_at_turn(
    self,
    drone_id: DroneId,
    path: list[ZoneAtTurn],
    turn: int,
) -> str | None:
```

返すものは次のどれかです。

```text
通常移動       → "D1-A"
goalへの移動   → "D1-goal"
restricted移動 → "D1-A-B"
待機           → None
その機体が関係しないターン → None
```

最後の表示は`Fly_in.py`が担当します。

```text
planned_paths = path_planner.plan_all()
simulation = Simulation(graph, planned_paths)
output_lines = simulation.run()

各output_lineをprint
```

実装順は、補助メソッドからではなく次の順です。

1. `__init__()`を完成させる
2. `run()`の大枠を書く
3. `run()`の中で必要になったところで`_movement_at_turn()`を作る
4. `Fly_in.py`から呼ぶ

次は`run()`の宣言とdocstringを追加し、その中で必要になる「最終ターンをどう求めるか」から進めましょう。"""