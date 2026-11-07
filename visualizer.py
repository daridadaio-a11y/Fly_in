import pygame

from graph import Graph
from renderer import Renderer
from models import TurnState
WIDTH, HEIGHT = 3000, 2000
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
    """ターン状態の操作と自動再生を管理するPygame画面。"""

    def __init__(self, graph: Graph, turn_states: list[TurnState]) -> None:
        """グラフと表示対象のターン状態を保存する。"""
        self.graph = graph
        self.turn_states = turn_states
        # turn_states内の現在表示している位置
        self.current_turn_index = 0
        # Trueなら自動再生、Falseなら一時停止
        self.is_playing = False
        # 自動再生で次のターンへ進むまでの時間(ミリ秒)
        self.turn_interval_ms = 1000
        # 次のターンの位置まで滑らかに移動する時間(ミリ秒)
        self.transition_duration_ms = 450
        # 最後に自動でターンを進めた時刻
        self.last_turn_time = 0

    def _handle_event(
            self,
            event: pygame.event.Event,
    ) -> bool:
        """キー・終了操作を処理し、実行を続けるか返す"""
        # 閉じるボタンが押されたか確認
        if event.type == pygame.QUIT:
            return False

        # キー入力以外のイベントでは状態を変更しない
        if event.type != pygame.KEYDOWN:
            return True
        # EscキーならVisualiserを終了する
        if event.key == pygame.K_ESCAPE:
            return False
        self._key_event(event)
        return True

    def _key_event(
            self,
            event: pygame.event.Event,
    ) -> None:
        """キーを処理する"""
        # Spaceで自動再生と一時停止を切り替える
        if event.key == pygame.K_SPACE:
            self.is_playing = not self.is_playing
            # 時間を更新し、スペースを押した瞬間に次ターンに行くのを防ぐ
            self.last_turn_time = pygame.time.get_ticks()
        # 右キーで次のターンへ進む
        elif event.key == pygame.K_RIGHT:
            self.is_playing = False
            # リストの最後の位置より少ない位置か確認
            if self.current_turn_index < len(self.turn_states) - 1:
                self.current_turn_index += 1
        # 左キーで前のターンへ戻る
        elif event.key == pygame.K_LEFT:
            self.is_playing = False

            if self.current_turn_index > 0:
                self.current_turn_index -= 1

        # Rキーで最初のターンへ戻る
        elif event.key == pygame.K_r:
            self.is_playing = False
            self.current_turn_index = 0

    def _update_auto_play(self) -> None:
        """再生中なら、指定時間ごとに次のターンへ進める"""
        # 一時停止中なら何もしない
        if not self.is_playing:
            return

        # pygame開始後から現在までの経過時間を取得する
        current_time = pygame.time.get_ticks()

        # 最後の更新から、設定した時間が立っていなければ何もしない
        elapsed_time = current_time - self.last_turn_time
        if elapsed_time < self.turn_interval_ms:
            return

        # 最後のターンに到達していたら自動再生を止める
        last_turn_index = len(self.turn_states) - 1
        if self.current_turn_index >= last_turn_index:
            self.is_playing = False
            return
        # 次のターンへ進む
        self.current_turn_index += 1

        # 今回進めた時刻を次の時間計測の開始点にする
        self.last_turn_time = current_time

    def make_pygame(self) -> None:
        """pygameのウィンドウを開き、終了操作を処理する。"""
        pygame.init()
        # ウィンドウサイズを変更できるようにする
        screen = pygame.display.set_mode(
            (WIDTH, HEIGHT),
            pygame.RESIZABLE,
        )
        pygame.display.set_caption("疲れたよパトラッシュ")
        # フレームレートの制御
        clock = pygame.time.Clock()
        renderer = Renderer(self.graph)

        self.last_turn_time = pygame.time.get_ticks()

        running = True
        # while一周が画面の１フレーム
        while running:
            # 入力処理
            for event in pygame.event.get():
                if self._handle_event(event) is False:
                    running = False
                    break
            # 終了操作を受けた場合は描画せずwhileを抜ける
            if not running:
                break

            # 必要な時間が経過していれば次のターンへ進める
            self._update_auto_play()
            # 背景の色
            screen.fill(NIGHT_BLUE)  # 前の画面を消す
            # 今表示するターン
            current_state = self.turn_states[self.current_turn_index]
            next_state = None
            transition_progress = 0.0
            if self.is_playing:
                next_index = self.current_turn_index + 1
                if next_index < len(self.turn_states):
                    next_state = self.turn_states[next_index]
                    elapsed_time = (
                        pygame.time.get_ticks() - self.last_turn_time
                    )
                    transition_progress = min(
                        elapsed_time / self.transition_duration_ms,
                        1.0,
                    )
            # 最後の状態が持っている、本当の最終ターン番号を取得する
            total_turns = self.turn_states[-1]["turn"]
            # 現在のターンを一度だけ描画する
            renderer.draw(
                screen,
                current_state,
                total_turns,
                next_state,
                transition_progress,
            )

            # 全てに変更を反映させ表示する
            pygame.display.update()
            # ループを一秒間に最大60回に制限する
            # これがないと何もなくとも高速でループし、CPUの無駄遣いになる
            clock.tick(60)

        pygame.quit()
