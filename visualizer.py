import pygame
from graph import Graph
WIDTH, HEIGHT = 1000, 700
# 色の設定
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
NIGHT = (20, 20, 50)
NIGHT_BLUE = (20, 24, 48)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)


class Visualizer:

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        (
            self.min_x,
            self.max_x,
            self.min_y,
            self.max_y,
        ) = self._get_map_bounds()

    def to_screen_position(
            self,
            map_x: int,
            map_y: int,
            screen_width: int,
            screen_height: int,
    ) -> tuple[int, int]:
        """地図座標をpygameの画面座標へ変換する。"""
        padding = 80  # 画面端の余白
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
            position1 = self.to_screen_position(
                zone1.x,
                zone1.y,
                WIDTH,
                HEIGHT,
            )
            position2 = self.to_screen_position(
                zone2.x,
                zone2.y,
                WIDTH,
                HEIGHT,
            )

            pygame.draw.line(
                screen,
                WHITE,
                position1,
                position2,
                3,
            )

    def _draw_zones(self, screen: pygame.Surface) -> None:
        """全ゾーンを種類に応じた色の円として描く"""
        for zone in self.graph.zones.values():
            position = self.to_screen_position(
                zone.x,
                zone.y,
                WIDTH,
                HEIGHT,
            )
            zone_type = zone.metadata["zone"]

            if zone.role == "start_hub:":
                color = GREEN
            elif zone.role == "end_hub:":
                color = YELLOW
            elif zone_type == "blocked":
                color = BLACK
            elif zone_type == "restricted":
                color = RED
            else:
                color = WHITE
            pygame.draw.circle(
                screen,  # 描画する画面
                color,  # 色指定
                position,  # 円の中心座標
                20,  # 円の半径
            )

    def make_pygame(self) -> None:
        """pygameのウィンドウを開き、終了操作を処理する。"""
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("疲れたよパトラッシュ")
        # フレームレートの制御
        clock = pygame.time.Clock()

        running = True
        # while一周が画面の１フレーム
        while running:
            # 入力処理
            for event in pygame.event.get():
                # 画面が閉じたら終了
                if event.type == pygame.QUIT:
                    running = False
            # 描画処理
            # 背景の色
            screen.fill(NIGHT_BLUE)  # 前の画面を消す
            # 接続を描画
            self._draw_connections(screen)
            # 円を描画
            self._draw_zones(screen)
            # 全てに変更を反映させる
            pygame.display.update()
            # ループを一秒間に最大60回に制限する
            # これがないと何もなくとも高速でループし、CPUの無駄遣いになる
            clock.tick(60)

        pygame.quit()
