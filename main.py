import pyxel
import json
import time
from enum import Enum

# 背景クラス
class Background:
    NUM_LINES = 20  # 星の数

    # 背景を初期化してゲームに登録する
    def __init__(self, game):
        self.game = game  # ゲームへの参照
        self.lines = []  # 水の線

        # 星の座標と速度を初期化してリストに登録する
        for i in range(Background.NUM_LINES):
            x = pyxel.rndi(0, pyxel.width - 1)  # X座標
            y = pyxel.rndi(0, pyxel.height - 1)  # Y座標
            # vy = pyxel.rndf(1, 2.5)  # Y方向の速度
            # vy = 1  # Y方向の速度
            h = pyxel.rndi(10, 20)  # 線の長さ
            self.lines.append((x, y, h))  # タプルとしてリストに登録

        # ゲームに背景を登録する
        self.game.background = self

    # 背景を更新する
    def update(self):
        for i, (x, y, h) in enumerate(self.lines):
            # y += vy
            y += self.game.flow_speed + self.game.flow_increase
            if y >= pyxel.height:  # 画面下から出たか
                y -= pyxel.height  # 画面上に戻す
                x = pyxel.rndi(0, pyxel.width - 1)
            self.lines[i] = (x, y, h)

    # 背景を描画する
    def draw(self):
        # タイトル画面以外で銀河を描画する
        # if self.game.scene != Game.TITLE:
        #     pyxel.blt(0, 0, 1, 0, 0, 120, 160)


        # キラキラを描画する
        if self.game.scene != Scene.TITLE:
            for i in range(3):
                pyxel.pset(pyxel.rndi(0, pyxel.width), pyxel.rndi(0, 60), 7)

        # 水の線を描画する
        for x, y, h in self.lines:
            # color = 7 if speed > 1.8 else 6  # 速度に応じて色を変える
            # pyxel.pset(x, y, color)
            pyxel.line(x, y, x, y+h, 6)

        # 上のグラデーション
        for i in range(3):
            pyxel.dither(1-(i+1)*0.25)
            pyxel.rect(0, 0+i*8, pyxel.width, 8, 7)
            pyxel.dither(1)

class Scene(Enum):
    TITLE = 0
    PLAY = 1
    GAMEOVER = 5

class Rock:

    def __init__(self, game):
        self.game = game
        self.x = pyxel.rndi(0, pyxel.width - 1)
        self.y = -16
        self.game.rocks.append(self)

    def update(self):
        self.y += self.game.flow_increase

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 16, 16, 16, 16, 12)

class Player:
    # JUMP_X = 
    MAX_X_SPEED = 1.5
    MAX_Y_SPEED = 1.5
    # DOWN_Y_SPEED = 1
    JUMP_X_DOWN_SPEED = 0.1
    JUMP_Y_DOWN_SPEED = 0.1

    LIMIT_LINE = 100 # 進める限界の地点

    # アニメーション用
    ANI_FRAME_COUNT = 2

    JDIR_RIGTH = 0
    JDIR_LEFT = 1

    MAX_RING_SIZE = 20

    def __init__(self, game):
        self.game = game
        self.x = pyxel.width / 2 - 8
        self.y = pyxel.height - 16
        self.vx = 0
        self.vy = 0
        self.is_jumping_dir = None

        # アニメーション用
        self.ani_frame = 0

        # 水の輪っか
        self.rings = []

        self.game.player = self

    def update(self):
        # 入力共通
        if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_LEFT):
            self.vx = self.MAX_X_SPEED
            self.vy = self.MAX_Y_SPEED

            # アニメーション
            self.ani_frame = pyxel.frame_count

            # 水の輪っかを追加
            self.rings.append((self.x+8, self.y+8, 5))

        # 右入力
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.is_jumping_dir = self.JDIR_RIGTH

        # 左入力
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.is_jumping_dir = self.JDIR_LEFT

        # LIMIT_LINEより前には行けないようにする
        # if self.y < self.LIMIT_LINE:
            # self.game.flow_speed += self.vy
            # self.vy = 0

        # 右へジャンプ中の場合
        if self.is_jumping_dir == self.JDIR_RIGTH:
            if self.x < pyxel.width-16-3:
                self.x += self.vx

        # 左へジャンプ中の場合
        if self.is_jumping_dir == self.JDIR_LEFT:
            if self.x > 3:
                self.x -= self.vx

        # ジャンプ中共通処理
        if self.is_jumping_dir is not None:
            if self.vx > 0:
                self.vx -= self.JUMP_X_DOWN_SPEED
            if self.vy > 0:
                self.vy -= self.JUMP_Y_DOWN_SPEED

            if self.y < self.LIMIT_LINE:
                self.game.flow_increase = self.vy
            else:
                self.y -= self.vy
            
            # これ以上ジャンプ中でいられない時
            if self.vx < self.JUMP_X_DOWN_SPEED and self.vy < self.JUMP_Y_DOWN_SPEED:
                self.vx = 0
                self.vy = 0
                if self.y < self.LIMIT_LINE:
                    self.game.flow_increase = 0
                # else:
                #     self.y -= self.vy

                self.is_jumping_dir = None

        # ジャンプしていない時共通処理
        if self.is_jumping_dir is None:
            if self.y < pyxel.height - 16:
                self.y += self.game.flow_speed

        # 水の輪の更新
        self.rings = [(x, y+self.game.flow_increase, s+1) for (x, y, s) in self.rings if s+1 < self.MAX_RING_SIZE]

    # def draw_resource(self):

    def draw(self):

        for (x, y, size) in self.rings:
            pyxel.circb(x, y, size, 6)
        # くっきりした影
        # pyxel.pal(3, 5)
        # pyxel.pal(11, 5)
        # pyxel.pal(10, 5)
        # pyxel.blt(self.x+1, self.y+1, 0, 16, 0, 16, 16, 6)
        # pyxel.pal()
        # 丸い影（のつもり）
        # pyxel.dither(0.5)
        # pyxel.circ(self.x+7, self.y+8, 8, 5)
        # pyxel.circ(self.x+8, self.y+8, 8, 5)
        # pyxel.dither(1)

        # 腕部分
        if self.ani_frame <= pyxel.frame_count < self.ani_frame+self.ANI_FRAME_COUNT*(1):
            pyxel.pal(3, 5)
            pyxel.pal(11, 5)
            pyxel.pal(10, 5)
            pyxel.blt(self.x-8+1, self.y-8+1, 0, 32, 0, 16, 16, 12)
            pyxel.blt(self.x+8+1, self.y-8+1, 0, 32, 0, -16, 16, 12)
            pyxel.pal()
            pyxel.blt(self.x-8, self.y-8, 0, 32, 0, 16, 16, 12)
            pyxel.blt(self.x+8, self.y-8, 0, 32, 0, -16, 16, 12)
        elif self.ani_frame+self.ANI_FRAME_COUNT*(1) <= pyxel.frame_count < self.ani_frame+self.ANI_FRAME_COUNT*(2):
            pyxel.pal(3, 5)
            pyxel.pal(11, 5)
            pyxel.pal(10, 5)
            pyxel.blt(self.x-8+1, self.y-8+1, 0, 48, 0, 16, 16, 12)
            pyxel.blt(self.x+8+1, self.y-8+1, 0, 48, 0, -16, 16, 12)
            pyxel.pal()
            pyxel.blt(self.x-8, self.y-8, 0, 48, 0, 16, 16, 12)
            pyxel.blt(self.x+8, self.y-8, 0, 48, 0, -16, 16, 12)
        elif self.ani_frame+self.ANI_FRAME_COUNT*(2) <= pyxel.frame_count < self.ani_frame+self.ANI_FRAME_COUNT*(3):
            pyxel.pal(3, 5)
            pyxel.pal(11, 5)
            pyxel.pal(10, 5)
            pyxel.blt(self.x-8+1, self.y-8+1, 0, 64, 0, 16, 16, 12)
            pyxel.blt(self.x+8+1, self.y-8+1, 0, 64, 0, -16, 16, 12)
            pyxel.pal()
            pyxel.blt(self.x-8, self.y-8, 0, 64, 0, 16, 16, 12)
            pyxel.blt(self.x+8, self.y-8, 0, 64, 0, -16, 16, 12)
        else:
            pyxel.pal(3, 5)
            pyxel.pal(11, 5)
            pyxel.pal(10, 5)
            pyxel.blt(self.x+1, self.y+1, 0, 16, 0, 8, 8, 12)
            pyxel.blt(self.x+8+1, self.y+1, 0, 16, 0, -8, 8, 12)
            pyxel.pal()
            pyxel.blt(self.x, self.y, 0, 16, 0, 8, 8, 12)
            pyxel.blt(self.x+8, self.y, 0, 16, 0, -8, 8, 12)
        
        # あし
        pyxel.pal(3, 5)
        pyxel.pal(11, 5)
        pyxel.pal(10, 5)
        pyxel.blt(self.x+1, self.y+8+1, 0, 16, 8, 8, 8, 12)
        pyxel.blt(self.x+8+1, self.y+8+1, 0, 16, 8, -8, 8, 12)
        pyxel.pal()
        pyxel.blt(self.x, self.y+8, 0, 16, 8, 8, 8, 12)
        pyxel.blt(self.x+8, self.y+8, 0, 16, 8, -8, 8, 12)

        # pyxel.blt(self.x, self.y, 0, 16, 0, 16, 16, 6)

        # pyxel.text(4, pyxel.height // 2, f"is_jumping_dir: {self.is_jumping_dir}", 13)
        # pyxel.text(4, pyxel.height // 2+8, f"vx: {self.vx}, vy: {self.vy}", 13)
        # pyxel.text(4, pyxel.height // 2+16, f"flow_speed: {self.game.flow_speed}", 13)



class Game:
    WIDTH = 120
    HEIGHT = 160
    def __init__(self):
        pyxel.init(self.WIDTH, self.HEIGHT, title="GO FROG")

        # pyxel.load("asset.pyxres")
        pyxel.load("asset.pyxres")

        self.background = None

        # シーン
        self.scene = None

        # 
        self.player = None
        self.enemys = []

        # 岩関係
        self.rocks = []
        self.rock_interval = 100
        self.rock_same_apper_count = 2
        self.last_rock = 0

        # 川の流れ関係
        self.traveled_distance = 0
        self.flow_speed = 0.5
        self.flow_increase = 0

        Background(self)
        Player(self)

        self.__change_scene(Scene.TITLE)
        pyxel.run(self.update, self.draw)

    
    def __change_scene(self, scene):
        """画面変更時に必ず行う初期化を行うメソッド
        """
        self.scene = scene
        if self.scene == Scene.TITLE:
            pass

        elif self.scene == Scene.PLAY:
            pass

        elif self.scene == Scene.GAMEOVER:
            pass

    def __update_title(self):
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.__change_scene(Scene.PLAY)
        
    def __update_play(self):
        self.player.update()
        # カエルが空間の位置的に進んでいるときにカウントする
        self.traveled_distance += self.flow_increase
        # カエルが川の流れに対して進んでいるときにカウントする
        # self.traveled_distance += self.player.vy

        if self.last_rock + self.rock_interval < int(self.traveled_distance):
            for _ in range(self.rock_same_apper_count):
                Rock(self)
            self.last_rock = int(self.traveled_distance)
        for rock in self.rocks:
            rock.update()

    def update(self):
        # Qキーで離脱
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.background.update()
        if self.scene == Scene.TITLE:
            self.__update_title()
        elif self.scene == Scene.PLAY:
            pass
            self.__update_play()
        elif self.scene == Scene.GAMEOVER:
            pass


    def __draw_title(self):

        self.__draw_bush()
        size_x = 72
        size_y = 40
        pyxel.rect(pyxel.width / 2 - size_x / 2, 40, size_x, size_y, 1)
        msg = "GO FROG"
        pyxel.text(pyxel.width / 2 - (len(msg) * pyxel.FONT_WIDTH // 2), pyxel.height / 2 - 10, msg, 7)

        msg = "enter to start"
        pyxel.text(pyxel.width / 2 - (len(msg) * pyxel.FONT_WIDTH // 2), 100, msg, 7)

    def __draw_play(self):
        
        # プレイヤーの描画
        self.player.draw()

        # 岩の描画
        for rock in self.rocks:
            rock.draw()

        self.__draw_bush()

        # SCORE
        pyxel.blt(8, 8, 0, 0, 32, 8, 16, 12)
        for i in range(7):
            pyxel.blt(16+(i*6), 8, 0, 5, 32, 6, 16, 12)
        pyxel.blt(16+(6*7), 8, 0, 8, 32, 8, 16, 12)

        for i in range(1, -1, -1):
            pyxel.text(13+i, 13+i, f"SCORE : {int(self.traveled_distance / 10)}", i if i else 7)

    def __draw_bush(self):
        # offset = (pyxel.frame_count // 8) % 160
        # for i in range(2):
        #     for x, y in self.near_cloud:
        #         pyxel.blt(x + i * 160 - offset, y, 0, 0, 32, 56, 8, 12)
        offset = self.traveled_distance % 16
        pyxel.text(60,60,f"offset: {offset}", 1)
        for i in range(-1, pyxel.height // 16):
            #左
            pyxel.pal(3, 5)
            pyxel.blt(1, 2 + 16 * i+offset, 0, 0, 16, 16, 16, 12)
            pyxel.pal()
            pyxel.blt(0, 0 + 16 * i+offset, 0, 0, 16, 16, 16, 12)
            #右
            pyxel.pal(3, 5)
            pyxel.blt(pyxel.width-16+1, 2 + 16 * i+offset, 0, 0, 16, -16, 16, 12)
            pyxel.pal()
            pyxel.blt(pyxel.width-16, 0 + 16 * i+offset, 0, 0, 16, -16, 16, 12)

    def draw(self):
        pyxel.cls(12)

        self.background.draw()
        # pyxel.text(4, 12, "in draw", 7)
        if self.scene == Scene.TITLE:
            self.__draw_title()
        elif self.scene == Scene.PLAY:
            self.__draw_play()
        elif self.scene == Scene.GAMEOVER:
            pass
            # self.__draw_gameover()
        pyxel.text(20, 0, f"x: {self.player.x}, y:{self.player.y}", 1)
        pyxel.text(20, 70, f"traveled_distance: {int(self.traveled_distance)}", 1)
        pyxel.text(20, 80, f"bool: {int(self.traveled_distance) % 10}", 1)
Game()