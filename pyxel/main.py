import pyxel
import webbrowser

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
            h = pyxel.rndi(10, 20)  # 線の長さ
            self.lines.append((x, y, h))  # タプルとしてリストに登録

        # ゲームに背景を登録する
        self.game.background = self

    # 背景を更新する
    def update(self):
        for i, (x, y, h) in enumerate(self.lines):
            y += self.game.flow_speed + self.game.flow_increase
            if y >= pyxel.height:  # 画面下から出たか
                y -= pyxel.height  # 画面上に戻す
                x = pyxel.rndi(0, pyxel.width - 1)
            self.lines[i] = (x, y, h)

    # 背景を描画する
    def draw(self):
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
        # 進み具合によって色をカエル
        # if self.game.traveled_distance < 600:
        #     col = 7
        # elif self.game.traveled_distance < 1000:
        #     col = 10
        # elif self.game.traveled_distance < 1500:
        #     col = 9
        # else:
        #     col = 8
        col = 7
        for i in range(3):
            pyxel.dither(1-(i+1)*0.25)
            pyxel.rect(0, 0+i*8, pyxel.width, 8, col)
            pyxel.dither(1)

class Scene():
    TITLE = 0
    PLAY = 1


class Rock:

    def __init__(self, game, x):
        self.game = game
        self.x = x
        self.y = -16
        self.game.rocks.append(self)

    def update(self):
        self.y += self.game.flow_increase

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 16, 16, 16, 16, 12)

        frame = pyxel.frame_count // 4 % 2
        if frame:
            pyxel.blt(self.x, self.y+8, 0, 16, 32, 16, 8, 7)
        else:
            pyxel.blt(self.x, self.y+8, 0, 16, 40, 16, 8, 7)
    
    def get_hit_area(self):
        return (self.x + 1, self.y + 8, 14, 5)

class Player:
    MAX_X_SPEED = 1.5
    MAX_Y_SPEED = 1.5
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
        click_left = False
        click_right = False
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if pyxel.mouse_x < pyxel.width / 2:
                click_left = True
            if pyxel.mouse_x > pyxel.width / 2:
                click_right = True

        # 入力共通
        if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_LEFT) or click_right or click_left:
            self.vx = self.MAX_X_SPEED
            self.vy = self.MAX_Y_SPEED

            # アニメーション
            self.ani_frame = pyxel.frame_count

            # 水の輪っかを追加
            self.rings.append((self.x+8, self.y+8, 5))

    
        # 右入力
        if pyxel.btnp(pyxel.KEY_RIGHT) or click_right:
            self.is_jumping_dir = self.JDIR_RIGTH

        # 左入力
        if pyxel.btnp(pyxel.KEY_LEFT) or click_left:
            self.is_jumping_dir = self.JDIR_LEFT

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

    def draw(self):

        for (x, y, size) in self.rings:
            pyxel.circb(x, y, size, 6)

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


class Game:
    WIDTH = 120
    HEIGHT = 176
    def __init__(self):
        pyxel.init(self.WIDTH, self.HEIGHT, title="GO FROG")

        pyxel.load("asset.pyxres")

        self.scene = None
        self.background = None

        # プレイヤーを定義
        self.player = None
        # self.enemys = []

        self.show_how_to = True

        #test
        pyxel.mouse(True)
        #test
        # ゲームの初期化
        self.__game_init()

        self.__change_scene(Scene.TITLE)
        pyxel.run(self.update, self.draw)

    def __game_init(self):

        # 岩関係
        self.rocks = []
        self.rock_interval = 0
        self.rock_same_apper_count = 1
        self.last_rock = 0

        # 川の流れ関係
        self.traveled_distance = 0 # 物理的に進んだ距離（カメラが動いた距離的な感じ）
        self.flow_speed = 0.5 # 川の流れの速さ
        self.flow_increase = 0 # カエルが進もうとしたときに追従する場合の、速度追加分

        self.game_over = False
        self.game_over_count = 0

        Background(self)
        Player(self)
    
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
        if pyxel.frame_count < 30:
            return
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.__change_scene(Scene.PLAY)

        if pyxel.btnp(pyxel.KEY_RETURN):
            self.__change_scene(Scene.PLAY)
        
    def __update_play(self):

        if self.game_over:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and (pyxel.width / 2 - 8 <= pyxel.mouse_x <= pyxel.width / 2 - 8 + 16) and (102 <= pyxel.mouse_y <= 102+16):
                # pyxel.width / 2 - 8, 102
                link = f"https://twitter.com/intent/tweet?text=GO%20FROG%E3%82%92%E3%83%97%E3%83%AC%E3%82%A4%E3%81%97%E3%81%BE%E3%81%97%E3%81%9F%E3%80%82%0A%E3%82%B9%E3%82%B3%E3%82%A2%E3%81%AF{int(self.traveled_distance / 10)}%E7%82%B9%E3%81%A7%E3%81%97%E3%81%9F%E3%80%82%0A%23pyxel%20%23python"
                webbrowser.open(link)
                return

            if self.game_over_count > 30:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.__game_init()
                if pyxel.btnp(pyxel.KEY_RETURN):
                    self.__game_init()
            
            self.game_over_count += 1
            return
        
        if self.show_how_to:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.show_how_to = False

            if pyxel.btnp(pyxel.KEY_RETURN):
                self.show_how_to = False
            return

        self.player.update()
        # カエルが空間の位置的に進んでいるときにカウントする
        self.traveled_distance += self.flow_increase
        # カエルが川の流れに対して進んでいるときにカウントする
        # self.traveled_distance += self.player.vy

        # 岩の生成
        if self.last_rock + self.rock_interval < int(self.traveled_distance):
            new_rock_x = []
            while len(new_rock_x) < self.rock_same_apper_count:
                new_x = pyxel.rndi(5, pyxel.width - 21)
                if all(abs(e - new_x) > 16 for e in new_rock_x):
                    Rock(self, new_x)
                    new_rock_x.append(new_x)
            self.last_rock = int(self.traveled_distance)

        # 難易度調整
        if int(self.traveled_distance) < 1:
            self.rock_interval = 0
        elif int(self.traveled_distance) < 100:
            self.rock_interval = 80
        elif int(self.traveled_distance) < 200:
            self.rock_same_apper_count = 2
        elif int(self.traveled_distance) < 300:
            pass
        elif int(self.traveled_distance) < 400:
            self.flow_speed = 1
        elif int(self.traveled_distance) < 500:
            self.flow_speed = 1.25
        elif int(self.traveled_distance) < 600:
            self.rock_interval = 70
        elif int(self.traveled_distance) < 700:
            self.rock_same_apper_count = 3
        elif int(self.traveled_distance) < 800:
            self.rock_interval = 60
            pass
        elif int(self.traveled_distance) < 900:
            pass
        elif int(self.traveled_distance) < 1000:
            self.rock_interval = 50
        elif int(self.traveled_distance) < 1100:
            self.flow_speed = 2
        elif int(self.traveled_distance) < 1200:
            pass
        elif int(self.traveled_distance) < 1300:
            self.rock_interval = 40
        elif int(self.traveled_distance) < 1400:
            pass
        elif int(self.traveled_distance) < 1500:
            self.rock_same_apper_count = 4

        # 画面外の石を消す
        rocks = [rock for rock in self.rocks if rock.y < pyxel.height]
        self.rocks = rocks
        # 石の更新
        for rock in self.rocks:
            rock.update()

        # 当たり判定
        # カエルの四角
        f_point = [
            (self.player.x+2, self.player.y+2),# 左上
            (self.player.x+16-2, self.player.y+2),# 右上
            (self.player.x+3, self.player.y+16-1),# 左下
            (self.player.x+16-3, self.player.y+16-1),# 右下
        ]
        for rock in self.rocks:
            rx, ry, rw, rh = rock.get_hit_area()
            for (px, py) in f_point:
                if rx < px < rx+rw and ry < py < ry+rh:
                    self.game_over = True


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
        pyxel.dither(pyxel.frame_count / 60)
        offset_list = [40,42,44,42]
        offset = offset_list[(pyxel.frame_count // 30) % 4]
        pyxel.blt(pyxel.width / 2 - size_x / 2, offset, 1, 0, 0, size_x, size_y, 12)
        pyxel.dither(1)

        msg = "ENTER or TAP to START"
        pyxel.text(pyxel.width / 2 - (len(msg) * pyxel.FONT_WIDTH // 2), 100, msg, 1)

        # msg = "2026 okapping"
        # pyxel.text(pyxel.width / 2 - (len(msg) * pyxel.FONT_WIDTH // 2), pyxel.height-8, msg, 1)

    def __draw_play(self):
        
        # プレイヤーの描画
        self.player.draw()

        # 岩の描画
        for rock in self.rocks:
            rock.draw()

        self.__draw_bush()

        # SCORE
        # pyxel.blt(8, 8, 0, 0, 32, 8, 16, 12)
        # for i in range(7):
        #     pyxel.blt(16+(i*6), 8, 0, 5, 32, 6, 16, 12)
        # pyxel.blt(16+(6*7), 8, 0, 8, 32, 8, 16, 12)

        pyxel.dither(0.9)
        pyxel.rect(0, 0, pyxel.width, 9, 1)
        pyxel.dither(1)
        # pyxel.rectb(0, 0, pyxel.width, 9, 6)

        for i in range(1, -1, -1):
            pyxel.text(13+i, 2+i, f"SCORE : {int(self.traveled_distance / 10)}", 1 if i else 7)


        if self.game_over:
            w = 60
            h = 70
            pyxel.rect(pyxel.width / 2 -  w / 2, pyxel.height / 2 - h / 2, w, h, 6)
            pyxel.rectb(pyxel.width / 2 -  w / 2, pyxel.height / 2 - h / 2, w, h, 1)
            # pyxel.rectb(14, 16, 92, 156, 1)
            msg = "GAME OVER"
            for i in range(1, -1, -1):
                pyxel.text(pyxel.width / 2 - (len(msg) * pyxel.FONT_WIDTH // 2), 64+i, msg, 8 if i else 0)
            msg = f"SCORE : {int(self.traveled_distance / 10)}"
            pyxel.text(pyxel.width / 2 - (len(msg) * pyxel.FONT_WIDTH // 2), 80, msg, 1)
            # width = pyxel.width / 2 - (len(msg) * pyxel.FONT_WIDTH // 2)
            pyxel.line(pyxel.width / 2 - (len(msg) * pyxel.FONT_WIDTH // 2), 86, pyxel.width / 2 - (len(msg) * pyxel.FONT_WIDTH // 2) + len(msg) * pyxel.FONT_WIDTH, 86, 1)

            msg = "SHARE"
            pyxel.text(pyxel.width / 2 - (len(msg) * pyxel.FONT_WIDTH // 2), 94, msg, 1)
            pyxel.blt(pyxel.width / 2 - 8, 102, 0, 16, 48, 16, 16, 7)


        if self.show_how_to:
            # 操作説明
            pyxel.rect(14, 16, 92, 156, 6)
            pyxel.rectb(14, 16, 92, 156, 1)

            pyxel.text(18, 20, f"HOW TO PLAY", 1)
            pyxel.line(18, 26, 20 + len("HOW TO PLAY") * pyxel.FONT_WIDTH, 26, 1)

            pyxel.text(18, 28, f"[ PC ]", 1)
            # pyxel.text(16, 54, f"KEY", 1)
            pyxel.rect(26, 38, 22, 9, 10)
            pyxel.rectb(26, 38, 22, 9, 1)
            pyxel.text(33, 40, f"<-", 1)
            pyxel.blt(30, 60, 0, 16, 0, 16, 16, 12)
            pyxel.blt(24, 54, 0, 0, 48, 8, 8, 12)

            pyxel.rect(66, 38, 22, 9, 14)
            pyxel.rectb(66, 38, 22, 9, 1)
            pyxel.text(73, 40, f"->", 1)
            pyxel.blt(70, 60, 0, 16, 0, 16, 16, 12)
            pyxel.blt(84, 54, 0, 0, 48, -8, 8, 12)

            pyxel.text(18, 80, f"[ SMART PHONE ]", 1)
            pyxel.rectb(38, 88, 40, 64, 1)
            pyxel.pset(38, 88, 6)
            pyxel.pset(77, 88, 6)
            pyxel.pset(38, 151, 6)
            pyxel.pset(77, 151, 6)
            pyxel.rectb(40, 90, 36, 52, 1)
            pyxel.circb(58, 146, 3, 1)
            
            pyxel.rect(42, 92, 15, 48, 10)
            pyxel.rectb(42, 92, 15, 48, 1)
            pyxel.text(46, 112, f"<-", 1)
            pyxel.rect(59, 92, 15, 48, 14)
            pyxel.rectb(59, 92, 15, 48, 1)
            pyxel.text(63, 112, f"->", 1)

            msg = "ENTER or TAP to START"
            pyxel.text(pyxel.width / 2 - (len(msg) * pyxel.FONT_WIDTH // 2), pyxel.height-16, msg, pyxel.rndi(0, 15))



    def __draw_bush(self):
        # offset = (pyxel.frame_count // 8) % 160
        # for i in range(2):
        #     for x, y in self.near_cloud:
        #         pyxel.blt(x + i * 160 - offset, y, 0, 0, 32, 56, 8, 12)
        offset = self.traveled_distance % 16
        # pyxel.text(60,60,f"offset: {offset}", 1)
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

        # pyxel.text(20, 70, f"bool: {(pyxel.width / 2 - 8 <= pyxel.mouse_x <= pyxel.width / 2 - 8 + 16) and (102 <= pyxel.mouse_y <= 102+16)}", 1)
        # pyxel.text(20, 70, f"traveled_distance: {int(self.traveled_distance)}", 1)
        # pyxel.text(20, 80, f"mouse_x: {pyxel.mouse_x}", 1)
        # pyxel.text(20, 90, f"MOUSE_BUTTON_LEFT: {pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)}", 1)
Game()