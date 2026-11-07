import pygame
from pathlib import Path
import math
import random
import pygame.freetype as freetype
from graph import Graph
from models import TurnState

BASE_WIDTH, BASE_HEIGHT = 1000, 700
BASE_PADDING = 80
BASE_TOP_PADDING = 170
BASE_BOTTOM_PADDING = 80
BASE_ZONE_RADIUS = 20
BASE_DRONE_RADIUS = 12
BASE_CONNECTION_WIDTH = 3
BASE_DRONE_SPACING = 28
BASE_ZONE_OUTLINE_WIDTH = 3
BASE_DRONE_OUTLINE_WIDTH = 2
BASE_STATUS_FONT_SIZE = 24
BASE_HELP_FONT_SIZE = 14
BASE_ZONE_LABEL_FONT_SIZE = 14
BASE_DRONE_FONT_SIZE = 14
MAX_DRONES_PER_ROW = 4
VERTICAL_SPREAD = 1.7
STAR_COUNT = 70
WHITE = (255, 255, 255)
PINK = (255, 192, 203)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (112, 112, 112)
SKYBLUE = (135, 206, 235)
ORANGE = (255, 166, 76)
ORANGE_GLOW = (255, 126, 68, 90)
PANEL_COLOR = (37, 42, 74, 215)
PANEL_BORDER_COLOR = (255, 192, 203, 230)


class Renderer:
    """ターン状態をPygame画面へ描画する。"""

    def __init__(self, graph: Graph) -> None:
        """グラフ、フォント、描画範囲、固定の星を準備する。"""
        self.graph = graph
        self.zone_radius_cache: dict[tuple[int, int], int] = {}
        star_random = random.Random(42)
        self.stars = [
            (
                star_random.random(),
                star_random.random(),
                star_random.choice((1, 1, 1, 2)),
            )
            for _ in range(STAR_COUNT)
        ]

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
        next_state: TurnState | None = None,
        transition_progress: float = 0.0,
    ) -> None:
        """接続、ゾーン、ドローン、文字を順番に描画"""
        self._draw_stars(screen)
        self._draw_connections(screen, current_state, next_state)
        self._draw_zones(screen)
        self._draw_hub_labels(screen)
        self._draw_drones(
            screen,
            current_state,
            next_state,
            transition_progress,
        )
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
        panel_padding = self._scale_size(14, scale)
        panel_x = self._scale_size(12, scale)
        panel_y = self._scale_size(38, scale)
        panel_width = self._scale_size(245, scale)
        panel_height = self._scale_size(88, scale)
        self._draw_panel(
            screen,
            pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            scale,
        )

        self.font.render_to(
            screen,  # どの画面に描くか
            (panel_x + panel_padding, round(55 * scale)),  # 座標
            turn_text,  # 表示する文字
            PINK,  # 文字色
            size=font_size,
        )

        delivered_count = current_state["delivered_count"]
        delivered_text = f"Delivered: {delivered_count}"
        self.font.render_to(
            screen,
            (panel_x + panel_padding, round(85 * scale)),
            delivered_text,
            PINK,
            size=font_size,
        )

        help_font_size = self._scale_size(BASE_HELP_FONT_SIZE, scale)
        help_text = (
            "Space: Play/Pause  Left/Right: Turn  "
            "R: Restart  Esc: Quit"
        )
        screen_height = screen.get_height()
        help_rect = self.font.get_rect(help_text, size=help_font_size)
        help_panel_width = help_rect.width + panel_padding * 2
        help_panel_height = help_rect.height + panel_padding
        help_panel_x = self._scale_size(12, scale)
        help_panel_y = (
            screen_height
            - help_panel_height
            - self._scale_size(12, scale)
        )
        self._draw_panel(
            screen,
            pygame.Rect(
                help_panel_x,
                help_panel_y,
                help_panel_width,
                help_panel_height,
            ),
            scale,
        )
        help_position = (
            help_panel_x + panel_padding,
            help_panel_y + panel_padding // 2,
        )
        self.font.render_to(
            screen,
            help_position,
            help_text,
            WHITE,
            size=help_font_size,
        )

    def _draw_panel(
            self,
            screen: pygame.Surface,
            rect: pygame.Rect,
            scale: float,
    ) -> None:
        """半透明の角丸パネルを画面へ描画する。"""
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        border_width = self._scale_size(2, scale)
        border_radius = self._scale_size(14, scale)
        pygame.draw.rect(
            panel,
            PANEL_COLOR,
            panel.get_rect(),
            border_radius=border_radius,
        )
        pygame.draw.rect(
            panel,
            PANEL_BORDER_COLOR,
            panel.get_rect(),
            width=border_width,
            border_radius=border_radius,
        )
        screen.blit(panel, rect.topleft)

    def _draw_stars(self, screen: pygame.Surface) -> None:
        """画面サイズに追従する固定の星空を描く。"""
        width, height = screen.get_size()
        scale = self._get_screen_scale(screen)
        for x_ratio, y_ratio, base_radius in self.stars:
            position = (
                round(x_ratio * width),
                round(y_ratio * height),
            )
            radius = self._scale_size(base_radius, scale)
            pygame.draw.circle(screen, WHITE, position, radius)

    def _get_screen_scale(self, screen: pygame.Surface) -> float:
        """基準画面に対する現在の画面サイズの倍率を返す。"""
        screen_width, screen_height = screen.get_size()
        width_scale = screen_width / BASE_WIDTH
        height_scale = screen_height / BASE_HEIGHT
        return min(width_scale, height_scale)

    def _scale_size(self, base_size: int, scale: float) -> int:
        """基準サイズを画面倍率に合わせ、最低1ピクセルにする。"""
        return max(1, round(base_size * scale))

    def _get_zone_radius(self, screen: pygame.Surface) -> int:
        """密なマップでも接続が見えるゾーン半径を返す。"""
        screen_size = screen.get_size()
        cached_radius = self.zone_radius_cache.get(screen_size)
        if cached_radius is not None:
            return cached_radius

        scale = self._get_screen_scale(screen)
        base_radius = self._scale_size(BASE_ZONE_RADIUS, scale)
        minimum_distance: float | None = None

        for connection in self.graph.connections.values():
            zone1 = self.graph.zones[connection.zone1]
            zone2 = self.graph.zones[connection.zone2]
            position1 = self._to_screen_position(zone1.x, zone1.y, screen)
            position2 = self._to_screen_position(zone2.x, zone2.y, screen)
            distance = math.dist(position1, position2)
            if minimum_distance is None or distance < minimum_distance:
                minimum_distance = distance

        if minimum_distance is None:
            self.zone_radius_cache[screen_size] = base_radius
            return base_radius
        adaptive_radius = max(5, round(minimum_distance * 0.3))
        radius = min(base_radius, adaptive_radius)
        self.zone_radius_cache[screen_size] = radius
        return radius

    def _to_screen_position(
            self,
            map_x: int,
            map_y: int,
            screen: pygame.Surface,
    ) -> tuple[int, int]:
        """地図座標をpygameの画面座標へ変換する。"""
        screen_width, screen_height = screen.get_size()
        scale = self._get_screen_scale(screen)
        horizontal_padding = BASE_PADDING * scale
        top_padding = BASE_TOP_PADDING * scale
        bottom_padding = BASE_BOTTOM_PADDING * scale
        # 実際に使える画面の大きさ
        usable_width = screen_width - horizontal_padding * 2
        usable_height = screen_height - top_padding - bottom_padding
        # 渡されたマップ全体の幅と高さ
        map_width = self.max_x - self.min_x
        map_height = self.max_y - self.min_y
        visual_map_height = map_height * VERTICAL_SPREAD
        # 画面に収まる倍率の計算
        scale_x = usable_width / max(map_width, 1)
        scale_y = usable_height / max(visual_map_height, 1)
        # 画面からはみ出ないように小さい方の倍率を選ぶ
        scale = min(scale_x, scale_y)
        # マップの実際の描画高さを求める
        draw_widgh = map_width * scale
        draw_height = visual_map_height * scale
        # 余った空間の半分を開始位置にする
        offset_x = horizontal_padding + (usable_width - draw_widgh) / 2
        offset_y = top_padding + (usable_height - draw_height) / 2

        # マップの左端を０に揃える
        normalized_x = map_x - self.min_x
        # マップ座標をピクセルへ変換する
        scaled_x = normalized_x * scale
        screen_x = offset_x + scaled_x
        # y座標は上下を反転させる
        normalized_y = self.max_y - map_y
        scaled_y = normalized_y * scale * VERTICAL_SPREAD
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

    def _draw_connections(
            self,
            screen: pygame.Surface,
            current_state: TurnState,
            next_state: TurnState | None,
    ) -> None:
        """円同士をつなぐラインの描画"""
        scale = self._get_screen_scale(screen)
        line_width = self._scale_size(BASE_CONNECTION_WIDTH, scale)
        glow_width = line_width + self._scale_size(12, scale)
        glow_layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        glowing_connections = self._get_glowing_connections(
            current_state,
            next_state,
        )

        # restrictedゾーンへ移動中の接続の光を先に描く
        for connection in self.graph.connections.values():
            zone1 = self.graph.zones[connection.zone1]
            zone2 = self.graph.zones[connection.zone2]
            zone1_name, zone2_name = sorted(
                (connection.zone1, connection.zone2)
            )
            connection_key = (zone1_name, zone2_name)
            if connection_key not in glowing_connections:
                continue
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
            pygame.draw.line(
                glow_layer,
                ORANGE_GLOW,
                position1,
                position2,
                glow_width,
            )
        screen.blit(glow_layer, (0, 0))

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

            zone1_name, zone2_name = sorted(
                (connection.zone1, connection.zone2)
            )
            connection_key = (zone1_name, zone2_name)
            color = ORANGE if connection_key in glowing_connections else WHITE
            pygame.draw.line(
                screen,
                color,
                position1,
                position2,
                line_width
                + self._scale_size(2, scale)
                if color == ORANGE
                else line_width,
            )

    def _get_glowing_connections(
            self,
            current_state: TurnState,
            next_state: TurnState | None,
    ) -> set[tuple[str, str]]:
        """restrictedへ移動中または移動開始する接続を返す。"""
        states = [current_state]
        if next_state is not None:
            states.append(next_state)

        glowing_connections: set[tuple[str, str]] = set()
        for state in states:
            for location in state["drone_positions"].values():
                if location[0] != "connection":
                    continue
                destination_name = location[2]
                destination = self.graph.zones[destination_name]
                if destination.metadata["zone"] != "restricted":
                    continue
                zone1_name, zone2_name = sorted(
                    (location[1], destination_name)
                )
                glowing_connections.add((zone1_name, zone2_name))
        return glowing_connections

    def _draw_zones(self, screen: pygame.Surface) -> None:
        """全ゾーンを種類に応じた色の円として描く"""
        scale = self._get_screen_scale(screen)
        zone_radius = self._get_zone_radius(screen)
        glow_layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for zone in self.graph.zones.values():
            if zone.metadata["zone"] != "restricted":
                continue
            position = self._to_screen_position(zone.x, zone.y, screen)
            # 発光
            pygame.draw.circle(
                glow_layer,
                ORANGE_GLOW,
                position,
                zone_radius + self._scale_size(12, scale),
            )
        screen.blit(glow_layer, (0, 0))

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
                # 未認識色の場合だけ、ハブの役割に応じた色で代用する
                if zone.role == "start_hub:":
                    color = GREEN
                elif zone.role == "end_hub:":
                    color = YELLOW
                else:
                    color = GRAY
            outline_width = self._scale_size(
                BASE_ZONE_OUTLINE_WIDTH,
                scale,
            )
            outline_color = (
                ORANGE
                if zone.metadata["zone"] == "restricted"
                else WHITE
            )
            pygame.draw.circle(
                screen,
                outline_color,
                position,
                zone_radius + outline_width,
            )
            pygame.draw.circle(
                screen,  # 描画する画面
                color,  # 色指定
                position,  # 円の中心座標
                zone_radius,  # 円の半径
            )

    def _draw_hub_labels(
            self,
            screen: pygame.Surface,
    ) -> None:
        """開始・終了ゾーンの丸の直下にラベルを固定表示する。"""
        scale = self._get_screen_scale(screen)
        zone_radius = self._get_zone_radius(screen)
        font_size = self._scale_size(BASE_ZONE_LABEL_FONT_SIZE, scale)

        for zone in self.graph.zones.values():
            if zone.role == "start_hub:":
                label = "START"
            elif zone.role == "end_hub:":
                label = "GOAL"
            else:
                continue

            zone_position = self._to_screen_position(zone.x, zone.y, screen)
            text_rect = self.font.get_rect(label, size=font_size)
            text_rect.midtop = (
                zone_position[0],
                zone_position[1] + zone_radius + round(4 * scale),
            )
            self.font.render_to(
                screen,
                text_rect,
                label,
                WHITE,
                size=font_size,
            )

    def _draw_drones_zone(
            self,
            screen: pygame.Surface,
            location: tuple[str, ...],
    ) -> tuple[int, int]:
        """ゾーン上にいるドローンの基準座標を返す。"""
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
            next_state: TurnState | None,
            transition_progress: float,
    ) -> None:
        """現在位置から次の位置へ補間してドローンとIDを描画する。"""
        current_positions = self._get_drone_draw_positions(
            screen,
            current_state,
        )
        next_positions = current_positions
        if next_state is not None:
            next_positions = self._get_drone_draw_positions(
                screen,
                next_state,
            )

        progress = max(0.0, min(transition_progress, 1.0))
        smooth_progress = progress * progress * (3 - 2 * progress)

        for drone_id, current_position in current_positions.items():
            next_position = next_positions.get(drone_id, current_position)
            position = (
                round(
                    current_position[0]
                    + (next_position[0] - current_position[0])
                    * smooth_progress
                ),
                round(
                    current_position[1]
                    + (next_position[1] - current_position[1])
                    * smooth_progress
                ),
            )
            self._draw_drone(screen, drone_id, position)

    def _get_drone_draw_positions(
            self,
            screen: pygame.Surface,
            state: TurnState,
    ) -> dict[int, tuple[int, int]]:
        """1行最大4機の配置で各ドローンの描画座標を返す。"""
        drone_positions = state["drone_positions"]

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

        draw_positions: dict[int, tuple[int, int]] = {}
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
            # 1行最大4機にし、複数行を基準座標の上下へ配置する
            row_count = (
                len(drone_ids) + MAX_DRONES_PER_ROW - 1
            ) // MAX_DRONES_PER_ROW
            for index, drone_id in enumerate(drone_ids):
                row_index = index // MAX_DRONES_PER_ROW
                column_index = index % MAX_DRONES_PER_ROW
                row_start = row_index * MAX_DRONES_PER_ROW
                drones_in_row = min(
                    MAX_DRONES_PER_ROW,
                    len(drone_ids) - row_start,
                )
                start_x = (
                    base_position[0]
                    - ((drones_in_row - 1) * spacing) // 2
                )
                start_y = (
                    base_position[1]
                    - ((row_count - 1) * spacing) // 2
                )
                position = (
                    start_x + column_index * spacing,
                    start_y + row_index * spacing,
                )
                draw_positions[drone_id] = position
        return draw_positions

    def _draw_drone(
            self,
            screen: pygame.Surface,
            drone_id: int,
            position: tuple[int, int],
    ) -> None:
        """白い縁取り付きのドローンとIDを描画する。"""
        scale = self._get_screen_scale(screen)
        zone_radius = self._get_zone_radius(screen)
        drone_radius = min(
            self._scale_size(BASE_DRONE_RADIUS, scale),
            max(5, zone_radius - self._scale_size(3, scale)),
        )
        outline_width = self._scale_size(BASE_DRONE_OUTLINE_WIDTH, scale)
        drone_font_size = min(
            self._scale_size(BASE_DRONE_FONT_SIZE, scale),
            max(8, drone_radius + self._scale_size(2, scale)),
        )
        color = PINK if drone_id % 2 == 0 else SKYBLUE

        pygame.draw.circle(
            screen,
            WHITE,
            position,
            drone_radius + outline_width,
        )
        pygame.draw.circle(screen, color, position, drone_radius)

        drone_text = f"D{drone_id}"
        text_rect = self.font.get_rect(
            drone_text,
            size=drone_font_size,
        )
        text_rect.center = position
        self.font.render_to(
            screen,
            text_rect,
            drone_text,
            WHITE,
            size=drone_font_size,
        )
