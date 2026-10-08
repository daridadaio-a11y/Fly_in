# ReservationTable2 学習メモ

## 判断基準

1. `fly_in_drones_translation.pdf`
2. `Fly-in レビュー項目 .pdf`
3. 現在のソースコード

`reservation_table.py`と`project_status.txt`は過去の設計案であり、要件の根拠にはしない。

## 現在地

- `ReservationTable`は`Graph`だけを受け取る。
- ゾーン予約のキーは`(zone_name, turn)`。
- 接続予約のキーは`(source, destination, turn)`。
- 辞書の値は、予約しているドローンIDの集合`set[DroneId]`。
- `can_use_zone()`は次を判定できる状態。
  - `blocked`は使用不可。
  - startとgoalは容量無制限。
  - 通常のゾーンは、予約済みID数が`max_drones`未満なら使用可能。
- 不正な`zone_name`と負の`turn`は、将来の呼び出し側で防ぐ方針。

## 次にやること

ゾーン予約を実際に追加する処理を考える。

想定する入力:

- `zone_name`
- `turn`
- `drone_id`

考える順番:

1. `(zone_name, turn)`を予約辞書のキーにする。
2. キーがなければ空のID集合を用意する。
3. その集合へ`drone_id`を追加する。
4. `can_use_zone()`で使用可能と判定した後だけ予約する責務を、呼び出し側と予約表のどちらに置くか決める。

## 後で直す表記・品質項目

- `droneid`を`reserved_drone_ids`などへ変更する。
- docstring直前の空行を削除する。
- `Id`ではなく`ID`と表記する。
- 長い型エイリアスと型注釈をflake8に合わせて改行する。
- クラスと`__init__`へdocstringを追加する。
- A-BとB-Aが同じ接続容量を共有するよう、接続キーの順序を統一する。

