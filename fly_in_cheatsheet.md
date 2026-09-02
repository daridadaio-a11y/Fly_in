# 🛸 Fly-in Drones 開発リファレンス・チートシート

```
[マップファイル] 
       │
       ▼
 1. Parser & Validator ──▶ 2. Graph (静的) ──▶ 3. Space-Time (時間軸) ──▶ 4. Pathfinder ──▶ 5. Simulation (標準出力)
```

---

## 1. モジュール別 責務・入出力一覧

| モジュール | 主な役割・責務 | 入力 | 出力 |
| :--- | :--- | :--- | :--- |
| **① Parser & Validator**<br>`parser.py` | ・ファイル読み込み（`with open`）<br>・構文解析（空行/コメント除去、メタデータ辞書化）<br>・**整合性検証（ガードマン）** | `.txt` マップファイル | `MapData`<br>(ドローン数, Zone一覧, Connection一覧) |
| **② Graph (静的網)**<br>`graph.py`, `models.py` | ・外部ライブラリ不使用の独自グラフ構造<br>・隣接リスト（Adjacency List）の構築<br>・ゾーン情報・接続情報の保持 | `MapData` | `Graph` オブジェクト<br>(ノード・エッジ・隣接辞書) |
| **③ Space-Time (時間軸)**<br>`time_space.py` | ・各ターン $t$ の**リソース占有状況（予約管理）**<br>・ターン進行に伴う容量解放の判定<br>・制限ゾーン（2ターン移動）の飛行中追跡 | `Graph`, ターン数 $t$ | 予約テーブル / 占有チェッカー<br>(ゾーン・接続の空き判定) |
| **④ Pathfinder**<br>`pathfinder.py` | ・全ドローンの移動経路・待機スケジューリング<br>・複数ルートへの分散（ボトルネック回避）<br>・デッドロック（膠着状態）防止 | `Graph`, 予約テーブル | 全ドローンの行動計画<br>(各ターンの移動/待機リスト) |
| **⑤ Simulation & Output**<br>`simulation.py` | ・計画に基づくターン進行と最終検証<br>・**仕様通りの標準出力フォーマット生成**<br>・ターミナルでの色付き表示（視覚化） | 行動計画 | 標準出力（1行1ターン）<br>`D1-zoneA D2-zoneB ...` |

---

## 2. 押さえるべき絶対ルール＆仕様

### ① ゾーン＆接続ルール
* **容量制限（Capacity）**:
  * 各ゾーンには同時滞在可能数（`max_drones`、デフォルト1）がある。※`start_hub` と `end_hub` は無制限。
  * 各接続にも同時通過可能数（`max_link_capacity`、デフォルト1）がある。
* **容量の即時解放**:
  * ターン $t$ にゾーン $A$ から別の場所へ移動するドローンがいる場合、**同じターン $t$ にゾーン $A$ へ進入するドローンは空いた枠を利用可能**。
* **ゾーン種別（Zone Types）**:
  * `normal`: 移動コスト 1 ターン。
  * `restricted`: 移動コスト **2 ターン**（1ターン目は接続上 `D<ID>-<connection>` を占有、2ターン目に目的ゾーンへ到着。途中で待機不可）。
  * `priority`: 優先通過ゾーン（経路選択で優遇）。
  * `blocked`: **進入不可**（グラフ構築時または探索時に完全除外）。

### ② 出力フォーマット（厳密遵守）
* **1行 = 1シミュレーションターン**。
* **動いたドローンのみ出力**（スペース区切り）: `D<ID>-<目的地>`
  * 例: `D1-corridor D2-roomA`
  * 制限ゾーンへ移動中の場合: `D1-roomA-roomB`
* **待機したドローンは出力しない**（行に含めない）。
* **ゴール（`end_hub`）に到達したドローンは完了**となり、以降のターンには出力しない。

---

## 3. 推奨データ構造（`models.py`）

標準ライブラリの `@dataclass` を活用した軽量かつ型安全な設計モデルです。

```python
from dataclasses import dataclass, field

@dataclass
class Zone:
    name: str
    role: str               # "start", "end", "normal"
    x: int
    y: int
    zone_type: str = "normal"  # "normal", "restricted", "priority", "blocked"
    max_drones: int = 1        # start/end は float('inf') など
    color: str = "white"

@dataclass(frozen=True)
class Connection:
    zone1: str
    zone2: str
    max_link_capacity: int = 1

    def get_other(self, current: str) -> str:
        """現在のゾーンの反対側を返すヘルパー"""
        return self.zone2 if current == self.zone1 else self.zone1

@dataclass
class Graph:
    zones: dict[str, Zone] = field(default_factory=dict)
    adjacency: dict[str, list[Connection]] = field(default_factory=dict)
    start_zone: Zone | None = None
    end_zone: Zone | None = None
```

---

## 4. パーサー＆バリデータ（ガードマン）のチェックリスト

- [ ] `nb_drones:` が正の整数（1以上）で存在するか。
- [ ] `start_hub:` と `end_hub:` が**それぞれ厳密に1つずつ**存在するか。
- [ ] ゾーン名にハイフン（`-`）や空白などの不正な文字が含まれていないか。
- [ ] ゾーン名が重複していないか。
- [ ] `connection:` で指定された2つのゾーンが、すでに定義済みのゾーンであるか（ゴースト部屋の排除）。
- [ ] 接続の重複（`A-B` と `B-A`）がないか。
- [ ] 属性値（`zone=...`, `max_drones=...` 等）のスペル・型・正負が正しいか。
- [ ] 不正入力時、トレースバック（Pythonの生エラー）を出さずに**明確なエラーメッセージを出して安全に終了**できるか。
