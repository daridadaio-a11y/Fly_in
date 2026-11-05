import pygame
from pathlib import Path
import pygame._freetype as freetype
from graph import Graph
from models import TurnState

BASE_WIDTH, BASE_HEIGHT = 1000, 700
BASE_PADDING = 80
BASE_ZONE_RADIUS = 20
BASE_DRONE_RADIUS = 12
BASE_CONNECTION_WIDTH = 3
BASE_DRONE_SPACING = 28
BASE_STATUS_FONT_SIZE = 24
BASE_DRONE_FONT_SIZE = 14
WHITE = (255, 255, 255)
PINK = (255, 192, 203)
BLUE = (0, 0, 255)


class Renderer:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

        # FreeTypeがすでに初期化されているか確認
        if not freetype.get_init():
            freetype.init()

        # 読み込みフォント
        font_path = Path(__file__).parent.joinpath(
            "assets",
            "fonts",
            "CherryBombOne-Regular.ttf",
        )
        self.font = freetype.Font(str(font_path), 24)
        (
            self.min_x,
            self.max_x,
            self.min_y,
            self.max_y,
        ) = self._get_map_bounds()

    def draw(
        self,
        screen: pygame.Surface,
        current_state: TurnState,
        total_turns: int,
    ) -> None:
        """接続、ゾーン、ドローン、文字を順番に描画"""
        self._draw_connections(screen)
        self._draw_zones(screen)
        self._draw_drones(screen, current_state)
        self._draw_status_panel(screen, current_state, total_turns)

    def _draw_status_panel(
        self,
        screen: pygame.Surface,
        current_state: TurnState,
        total_turns: int,
    ) -> None:
        """現在のターンと配達済みドローン数を表示する"""
        scale = self._get_screen_scale(screen)
        font_size = self._scale_size(BASE_STATUS_FONT_SIZE, scale)
        turn = current_state["turn"]
        turn_text = f"Turn: {turn} / {total_turns}"

        self.font.render_to(
            screen,  # どの画面に描くか
            (round(20 * scale), round(55 * scale)),  # 座標
            turn_text,  # 表示する文字
            PINK,  # 文字色
            size=font_size,
        )

        delivered_count = current_state["delivered_count"]
        delivered_text = f"Delivered: {delivered_count}"
        self.font.render_to(
            screen,
            (round(20 * scale), round(85 * scale)),
            delivered_text,
            PINK,
            size=font_size,
        )

    def _get_screen_scale(self, screen: pygame.Surface) -> float:
        """基準画面に対する現在の画面サイズの倍率を返す。"""
        screen_width, screen_height = screen.get_size()
        width_scale = screen_width / BASE_WIDTH
        height_scale = screen_height / BASE_HEIGHT
        return min(width_scale, height_scale)

    def _scale_size(self, base_size: int, scale: float) -> int:
        """基準サイズを画面倍率に合わせ、最低1ピクセルにする。"""
        return max(1, round(base_size * scale))

    def _to_screen_position(
            self,
            map_x: int,
            map_y: int,
            screen: pygame.Surface,
    ) -> tuple[int, int]:
        """地図座標をpygameの画面座標へ変換する。"""
        screen_width, screen_height = screen.get_size()
        scale = self._get_screen_scale(screen)
        padding = BASE_PADDING * scale  # 画面端の余白
        # 実際に使える画面の大きさ
        usable_width = screen_width - padding * 2
        usable_height = screen_height - padding * 2
        # 渡されたマップ全体の幅と高さ
        map_width = self.max_x - self.min_x
        map_height = self.max_y - self.min_y
        # 画面に収まる倍率の計算
        scale_x = usable_width / max(map_width, 1)
        scale_y = usable_height / max(map_height, 1)
        # 画面からはみ出ないように小さい方の倍率を選ぶ
        scale = min(scale_x, scale_y)
        # マップの実際の描画高さを求める
        draw_widgh = map_width * scale
        draw_height = map_height * scale
        # 余った空間の半分を開始位置にする
        offset_x = (screen_width - draw_widgh) / 2
        offset_y = (screen_height - draw_height) / 2

        # マップの左端を０に揃える
        normalized_x = map_x - self.min_x
        # マップ座標をピクセルへ変換する
        scaled_x = normalized_x * scale
        screen_x = offset_x + scaled_x
        # y座標は上下を反転させる
        normalized_y = self.max_y - map_y
        scaled_y = normalized_y * scale
        screen_y = offset_y + scaled_y

        return int(screen_x), int(screen_y)

    def _get_map_bounds(self) -> tuple[int, int, int, int]:
        """全ゾーンからマップ座標の最小値、最大値を調べて返す"""
        x_values: list[int] = []
        y_values: list[int] = []
        for zone in self.graph.zones.values():
            x_values.append(zone.x)
            y_values.append(zone.y)
        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)
        return (min_x, max_x, min_y, max_y)

    def _draw_connections(self, screen: pygame.Surface) -> None:
        """円同士をつなぐラインの描画"""
        for connection in self.graph.connections.values():
            zone1 = self.graph.zones[connection.zone1]
            zone2 = self.graph.zones[connection.zone2]
            position1 = self._to_screen_position(
                zone1.x,
                zone1.y,
                screen,
            )
            position2 = self._to_screen_position(
                zone2.x,
                zone2.y,
                screen,
            )

            scale = self._get_screen_scale(screen)
            line_width = self._scale_size(BASE_CONNECTION_WIDTH, scale)
            pygame.draw.line(
                screen,
                WHITE,
                position1,
                position2,
                line_width,
            )

    def _draw_zones(self, screen: pygame.Surface) -> None:
        """全ゾーンを種類に応じた色の円として描く"""
        for zone in self.graph.zones.values():
            position = self._to_screen_position(
                zone.x,
                zone.y,
                screen,
            )
            color_name = zone.metadata["color"]
            color: pygame.Color | tuple[int, int, int]
            if not isinstance(color_name, str):
                raise ValueError(f"Invalid color for zone '{zone.name}'.")
            try:
                # pygameが知っている色ならその色を使用
                color = pygame.Color(color_name)
            except ValueError:
                # pygameが知らない色なら青色で代用する
                color = BLUE
            scale = self._get_screen_scale(screen)
            zone_radius = self._scale_size(BASE_ZONE_RADIUS, scale)
            pygame.draw.circle(
                screen,  # 描画する画面
                color,  # 色指定
                position,  # 円の中心座標
                zone_radius,  # 円の半径
            )

    def _draw_drones_zone(
            self,
            screen: pygame.Surface,
            location: tuple[str, ...],
    ) -> tuple[int, int]:
        zone_name = location[1]
        zone = self.graph.zones[zone_name]

        position = self._to_screen_position(
            zone.x,
            zone.y,
            screen,
        )
        return position

    def _draw_drones_connection(
            self,
            screen: pygame.Surface,
            location: tuple[str, ...]
    ) -> tuple[int, int]:
        """ドローンが接続上にいる"""
        zone_name1 = location[1]
        zone_name2 = location[2]
        zone1 = self.graph.zones[zone_name1]
        zone2 = self.graph.zones[zone_name2]
        position1 = self._to_screen_position(
            zone1.x,
            zone1.y,
            screen,
        )
        position2 = self._to_screen_position(
            zone2.x,
            zone2.y,
            screen,
        )
        position = (
            (position1[0] + position2[0]) // 2,
            (position1[1] + position2[1]) // 2,
        )
        return position

    def _draw_drones(
            self,
            screen: pygame.Surface,
            current_state: TurnState,
    ) -> None:
        """現在位置にドローンとIDを描画する"""
        drone_positions = current_state["drone_positions"]

        # 場所ごとにそこにいるドローンIDをまとめる
        drones_by_location: dict[
            tuple[str, ...],
            list[int],
        ] = {}

        for drone_id, location in drone_positions.items():
            location_key: tuple[str, ...]
            # 接続はA→BとB→Aを同じ場所として扱う
            if location[0] == "connection":
                zone1, zone2 = sorted((location[1], location[2]))
                location_key = ("connection", zone1, zone2)
            else:
                location_key = location

            # 初めて出てきた場所なら、空のリストを用意する
            if location_key not in drones_by_location:
                drones_by_location[location_key] = []

            # その場所のリストへドローンIDを追加する
            drones_by_location[location_key].append(drone_id)
        # ドローンIDと位置情報を取得
        for location, drone_ids in drones_by_location.items():
            location_type = location[0]
            # ゾーンまたは接続の基準座標を取得する
            if location_type == "zone":
                base_position = self._draw_drones_zone(screen, location)
            elif location_type == "connection":
                base_position = self._draw_drones_connection(screen, location)

            # 想定していない位置形式なら描画しない
            else:
                continue
            # 画面サイズに合わせてドローンの大きさと間隔を変える
            scale = self._get_screen_scale(screen)
            spacing = self._scale_size(BASE_DRONE_SPACING, scale)
            drone_radius = self._scale_size(BASE_DRONE_RADIUS, scale)
            drone_font_size = self._scale_size(BASE_DRONE_FONT_SIZE, scale)
            # 複数機の中央が基準座標に来るようにする
            start_x = (
                base_position[0] - ((len(drone_ids) - 1) * spacing) // 2
            )
            # 同じ場所のドローンを1機ずつ描く
            for index, drone_id in enumerate(drone_ids):
                position = (
                    start_x + index * spacing,
                    base_position[1],
                )
                if drone_id % 2 == 0:
                    pygame.draw.circle(
                        screen,
                        PINK,
                        position,
                        drone_radius,
                    )
                else:
                    pygame.draw.circle(
                        screen,
                        BLUE,
                        position,
                        drone_radius,
                    )
                drone_text = f"D{drone_id}"
                # 文字が占める四角形を取得
                text_rect = self.font.get_rect(
                    drone_text,
                    size=drone_font_size,
                )
                # 文字の中心とドローン円の中心を合わせる
                text_rect.center = position

                self.font.render_to(
                    screen,
                    text_rect,
                    drone_text,
                    WHITE,
                    size=drone_font_size,
                )
