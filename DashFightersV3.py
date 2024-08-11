import pyxel
import random

# https://kitao.github.io/pyxel/wasm/launcher/?run=TadeKimura.DashFighters.DashFighters

#========== CLASS ==========#
class Game: #現在のゲーム状況にまつわる情報の保存
    isPlaying = False
    isSelecting = False
    isOver = False
    
    SPEED = 1.5

    ENEMYPOINTS = 100

    level = 1

    HIGHSCORE = 0

    def reset():
        buildings.clear() #リストに保存されてるデータを全て削除。
        enemies.clear()
        bullets.clear()
        emeralds.clear()
        chips.clear()

        for i in range(6): # range(x) x リストの中に作る建物のインスタンスの数の設定
            buildings.append(Building(i))
            enemies.append(Enemy())
            chips.append(Chip())


        Player.isAlive = True # キャラクターが死んだかどうかを確認するため
        Player.isGrounded = False # プレイヤーが地面に足がついてるかどうかを確認するため
        Player.isAttacking = False # プレイヤーが攻撃をしてるかどうかを確認するため。
        Player.canJump = False # 落下で敵を倒した時、一時的に、ジャンプがもう一回できる.
        Player.canBoost = False
        Player.isBoosting = False
        Player.boostTimer = 0

        Player.x = 48 # プレイヤーのX座標 プログラムでは、絶対変わらないが、調整が簡単のように変数で定義。
        Player.y = 72 #　プレイヤーの初期Y座標   
        Player.dy = 0 # プレイヤーの初期Yベクトル
        
        Player.framecount = 0
        Player.score = 0
        Game.level = 1

        Wand.charge = 46
        Wand.isRecharging = False
        Gun.ammo = 6
        Gun.isReloading = False

class Building: # 建てものに関するプログラムが全て含まれてるクラス
    LENGTH = [48, 64, 80] # 建物の種類によって、長さが違うので、そのデータをリストに保存   
    HEIGHT = [104,88, 72] # 建物の種類によって、高さが違うので、そのデータをリストに保存（小さい建物は、y座標が高い）
    bltX = [0, 80, 176] # assets.pyxres からのロードをする際に必要な情報.
    bltY = [8, 56, 128] # assets.pyxres からのロードをする際に必要な情報.

    def __init__(self, i):
        self.type = 1 # pyxres 参照: BUILDING A~C (0~2) の設定
        self.var = random.randint(0,2) # pyxres 参照: BUILDING 0~2 (0~2) の設定
        self.l = Building.LENGTH[self.var]

        self.x = 8 + i * 48
        self.y = Building.HEIGHT[self.type]

        self.GAP = 1
    
    def autogen(): #次の建物の種類、バリエーションと位置を定義するメソッド. 敵も、建物の一部として保存。
        for b in buildings:
            b.x += -2 * Game.SPEED #ゲームの進行状況により、スピードを上げるかも？

        for i in range(len(buildings)):
            if buildings[i].x <= -80: # 建物のx座標が-80になったとき実行
                if buildings[i-1].type == 0: # 前の建物がtype0（A)の時、次の建物は type 0~1 (A~B) のどちらかしか出てきてはいけない
                    buildings[i].type = random.randint(0,1)
                else: # 出なければ、何が出ても良い. このコードは無理ゲーにならないためのものです。
                    buildings[i].type = random.randint(0,2) 
                
                buildings[i].var = random.randint(0,2)
                buildings[i].l = Building.LENGTH[buildings[i].var]
                buildings[i].GAP = Building.gap(buildings[i].type, buildings[i-1].type)
                buildings[i].x = buildings[i-1].x + buildings[i-1].l + buildings[i].GAP - 2
                buildings[i].y = Building.HEIGHT[buildings[i].type]

                Enemy.setSpawnPos(i)
                Chip.setSpawnPos(i)

    def gap(a,b): # 建物と建物の間をランダムに設定。ただし無理ゲーになっては行けないので、場合わけされてます
        if a > b: # 前の建物が小さい場合、最大に出てくる数値が32px のギャップです
            return random.randint(0,2)* 12 * Game.SPEED
        if a == b:
            return random.randint(0,1)*24 * Game.SPEED
        else: # そのほかは、0~48 のギャップが出ます。
            return random.randint(0,2)*16 * Game.SPEED

    def update(): # 建物のx座標を徐々に左に動かす
        Building.autogen()

    def draw():
        for b in range(len(buildings)): # リストの情報とインスタンスのデータを利用し、建物を全て一つのラインで描くコード
            pyxel.blt(buildings[b].x, buildings[b].y-16, 1, Building.bltX[buildings[b].var], Building.bltY[buildings[b].type], buildings[b].l+16, 144 - buildings[b].y, 6 )
            # if buildings[b].GAP == 0:
            #     pyxel.line(buildings[b-1].x + buildings[b-1].l, buildings[b-1].y, buildings[b].x, buildings[b].y, 7)

class Player: #　プレイヤーに関するプログラムが全て含まれてるクラス。
    #========= キャラクター設定 =========#
    CHARACTER = 0 # 0:美剣, 1:ナタリー, 2:エメラルド ゲームプレイ設定、キャラクターごとに、ゲームプレイが変わるため、キャラクターの種類で場合分けするのに必要な変数。
    JUMP_POWER = -5.5
    
    isAlive = True # キャラクターが死んだかどうかを確認するため
    isGrounded = False # プレイヤーが地面に足がついてるかどうかを確認するため
    isAttacking = False # プレイヤーが攻撃をしてるかどうかを確認するため。
    canJump = False # 落下で敵を倒した時、一時的に、ジャンプがもう一回できる.
    canBoost = False
    isBoosting = False

    x = 48 # プレイヤーのX座標 プログラムでは、絶対変わらないが、調整が簡単のように変数で定義。
    y = 72 #　プレイヤーの初期Y座標   
    dy = 0 # プレイヤーの初期Yベクトル
    
    score = 0 # スコアが上がるごとに、難易度を上げたりゲームの流れのスピードを変える。
    
    framecount = 0
    boostTimer = 0

    def groundCollision(): 
        for b in buildings: #リストに入ってるインスタンスの全てに対して：
            if b.x-8 <= Player.x < b.x + b.l+2: #プレイヤーのポジションが、建物iとその長さの間にある場合実行。
                if b.y+8 >= Player.y+16 >= b.y: #プレイヤーのポジションが、建物の屋上と8pxの間にいる場合実行
                    Player.y = b.y - 16
                    Player.dy = 0
                    Player.isGrounded = True
                    Player.canJump = False

            elif b.x + b.l <= Player.x <= b.x + b.l+4 and Player.isGrounded: #プレイヤーが建物のより、２px以上８px以下右に行った場合実行。
                Player.isGrounded = False
                Player.canJump = False

    def objectCollision():
        for e in enemies: ##敵とぶつかったときに敵の位置とプレイヤーの位置を判定するコード
            if Player.x+6 <= e.x <= Player.x+9 and e.y <= Player.y + 8 <= e.y+8 and e.isAlive:
                Player.isAlive = False
                pyxel.play(0,8)

        for b in buildings: ##建物の壁とぶつかったときに敵の位置とプレイヤーの位置を判定するコード
            if b.x+4 <= Player.x+16 <= b.x + 20 and  b.y == Player.y:
                Player.isAlive = False
                pyxel.play(0,8)

        if Player.y > 144: # プレイヤーが画面の下にいったっばい実行
            Player.isAlive = False

        for c in chips: ##チップとぶつかったときに敵の位置とプレイヤーの位置を判定するコード
            if Player.x <= c.x+3 <= Player.x+16 and Player.y <= c.y+3 <= Player.y+16 and c.isAvailable:
                c.isAvailable = False
                Player.canBoost = True
                Player.boostTimer = 30 * (Game.level if Game.level <= 10 else 10)
                Player.score += 100
                Player.checkScore()
                pyxel.play(1,0)

    
    def Kick():
        for e in enemies: #プレイヤーがジャンプしたのち、敵がプレイヤーのしたにいる場合、敵のisAlive=Falseになる
            if Player.x - 8 <= e.x <= Player.x + 16 and e.y-2 <= Player.y + 16 <= e.y+8 and Player.dy >= 0 and e.isAlive:
                e.isAlive = False
                Player.dy = Player.JUMP_POWER
                Player.y += Player.dy
                Player.canJump = True
                pyxel.play(3,7)


    def Gravity():
        if Player.isGrounded == False and Player.dy <= 6: #キャラの重力計算.地に足がついてない時だけに実行
            Player.dy += 0.56
            Player.y += Player.dy
        elif Player.isGrounded == False and Player.dy > 6:
            Player.dy = 6
            Player.y += Player.dy
        elif Player.isAlive == False:
            Player.dy += 0.56
            Player.y += Player.dy

    def checkScore(): ##スコアのアップデート
        if Player.score % 1000 == 0 and Game.level != 1 or Player.score == 1000:
            if Game.level < 10:
                Game.level += 1

            else:
                Game.level += 1
                enemies.append(Enemy())

    def update():
        Player.groundCollision()
        Player.Gravity()

        Player.objectCollision()
        Player.Kick()

        if pyxel.btnp(pyxel.KEY_F) and Player.isBoosting == False: #攻撃する時に発動、キャラごとに変わる。
            if Player.CHARACTER == 0:
                Player.isAttacking = True
                Katana.slice()
                pyxel.play(0,1)
            elif Player.CHARACTER == 1 and Gun.isReloading == False:
                Player.isAttacking = True
                bullets.append(Gun())
                pyxel.play(0,2)

            elif Player.CHARACTER == 2 and Wand.isRecharging == False:
                Player.isAttacking = True
                Wand.set()
                pyxel.play(0,5)

                
        if pyxel.btn(pyxel.KEY_J) and (Player.isGrounded == True or Player.canJump): #ボタンJでキャラが地面に足がついてる時だけ押したときに実行。
            Player.isGrounded = False
            Player.dy = Player.JUMP_POWER
            Player.y += Player.dy

            pyxel.play(2,6)

            if Player.canJump == True:
                Player.canJump = False

        if Player.canBoost and Player.isBoosting == False: #チップを得たときにブーストする。
            Player.isBoosting = True
            Player.canBoost = False


        if Player.boostTimer != 0 and Player.isBoosting: #ブーストの時間の長さとの定義とアップデート
            Player.boostTimer -= 1
            if Player.CHARACTER == 0:
                Player.isAttacking = True
                Katana.slice()
                pyxel.play(0,1)
            elif Player.CHARACTER == 1:
                Player.isAttacking = True
                bullets.append(Gun())
                pyxel.play(0,2)
                Gun.ammo = 6
            elif Player.CHARACTER == 2:
                Player.isAttacking = True
                Wand.set()
                Wand.charge = 46

        elif Player.boostTimer == 0 and Player.isBoosting: 
            Player.isBoosting = False

        # if pyxel.btnp(pyxel.KEY_C): #DEBUG ようにキャラ変更
        #     if Player.CHARACTER != 2:
        #         Player.CHARACTER += 1
        #     else:
        #         Player.CHARACTER = 0
        
        if Player.isAttacking == True: #アニメーション用に使用。framecountピクセルのを使うより、自分のを使う。
            Player.framecount += 0.2
            if Player.framecount >= 3.6:
                Player.framecount = 0
                Player.isAttacking = False

        if Player.CHARACTER == 1: #キャラごとに、攻撃のコードが違うので、場合わけでアップデート。
            Gun.update()
        elif Player.CHARACTER == 2:
            Wand.update()

        if Player.isAlive == False: #プレイヤーが死んだときに発動。
            Player.isGrounded = False
            Player.dy = -5
            Player.y += Player.dy

            if Player.score > Game.HIGHSCORE:
                Game.HIGHSCORE = Player.score 

            Game.isOver = True

    def draw():
        # if Player.isAlive:
            if Player.CHARACTER == 1:
                Gun.draw()
            if Player.CHARACTER == 2:
                Wand.draw()

            if Player.isBoosting:
                pyxel.rect(Player.x, Player.y - 4, 16 * (Player.boostTimer/(30*Game.level)),2, 3)

            if Player.isAlive == False:
                Player.Gravity()
                Player.groundCollision()

                if Player.isGrounded == False:
                    Player.x += -1

                pyxel.blt(Player.x,Player.y+4, 0, 224,Player.CHARACTER *16, 16,16, 6)

            elif Player.isAttacking:
                pyxel.blt(Player.x,Player.y, 0, 96 + round(Player.framecount)*32,Player.CHARACTER *16, 32,16, 6)
            elif Player.isGrounded: #キャラクターが地に足がついている時の画像読み込み。frame_count でアニメーションを作る.
                pyxel.blt(Player.x,Player.y, 0, round(pyxel.frame_count*0.2)*16%96,Player.CHARACTER *16, 16,16, 6)
            elif Player.isGrounded == False:#キャラクターが地に足がついてない時の画像読み込み
                pyxel.blt(Player.x,Player.y, 0, 80,Player.CHARACTER*16, 16,16, 6)

class Enemy:
    def __init__(self):
        self.isAlive = True #敵が表示されるかどうかの真偽
        self.var = 0 #小型の種類が4つあるので、そこで、この var が使われる　見た目を変えるだけです。
        self.x = 0 #最初は皆、x座標を画面の外に作る
        self.y = -16
        self.framecount = 0

    def setSpawnPos(i):
        if 0 <= random.randint(0,100) <= Game.level * 10: #0~40 小型の敵が出てくる 41~100 敵が出てこない 40% の確率で出てくる
            enemies[i].x = buildings[i].x + buildings[i].l - random.randint(16,buildings[i].l-16) #x座標を建物の長さの中のどこかに動かす（最初と最後の16pxの中には表示しない
            enemies[i].y = buildings[i].y - 12
            enemies[i].var = 64 + random.randint(0,3)*8
            enemies[i].framecount = 0
            enemies[i].isAlive = True
        else:
            enemies[i].x = 0
            enemies[i].y = -16

        if Game.level > 10 and enemies[5+Game.level-10].x < 0:
            for d in range(Game.level - 10):
                enemies[5+d].x = buildings[i].x + buildings[i].l - random.randint(16,buildings[i].l-16) #x座標を建物の長さの中のどこかに動かす（最初と最後の16pxの中には表示しない
                enemies[5+d].y = buildings[i].y - 12
                enemies[5+d].var = 64 + random.randint(0,3)*8
                enemies[5+d].framecount = 0
                enemies[5+d].isAlive = True

    def update():
        for e in enemies:
            e.x += -2 * Game.SPEED

    def draw():
        for e in enemies:
            if e.isAlive == True:
                pyxel.blt(e.x+1, e.y-10 + round(pyxel.frame_count*0.05)%2, 0, 8,136, 6,6, 6)
                pyxel.blt(e.x,e.y, 0, round(pyxel.frame_count*0.1)*8%40,e.var, 8,8, 6) #敵が生きてる間のアニメーション
            elif e.isAlive == False:
                pyxel.blt(e.x,e.y, 0, 40 + round(e.framecount)*8,e.var, 8,8, 6) #敵が死んだ時のアニメーション
                e.framecount += 0.1
                if e.framecount <= 2:
                    pyxel.text(Player.x+18, Player.y - 5 - round(e.framecount)*2, '+' + str(Game.ENEMYPOINTS), 7)
            
class Chip:
    def __init__(self):
        self.isAvailable = True 
        self.x = 0 
        self.y = -16
        self.framecount = 0


    def setSpawnPos(i):
        if 0 <= random.randint(0,100) <= ((25 - Game.level * 2) if Game.level <= 10 else 5): #0~40 小型の敵が出てくる 41~100 敵が出てこない 40% の確率で出てくる
            chips[i].x = buildings[i].x + buildings[i].l - random.randint(16,buildings[i].l-16) #x座標を建物の長さの中のどこかに動かす（最初と最後の16pxの中には表示しない
            chips[i].y = buildings[i].y - 12
            chips[i].isAvailable = True
            chips[i].framecount = 0
        else:
            chips[i].x = 0
            chips[i].y = -16

    def update():
        for c in chips:
            c.x += -2 * Game.SPEED

    def draw():
        for c in chips:
            if c.isAvailable == True:
                pyxel.blt(c.x,c.y + round(pyxel.frame_count*0.05)%2, 0, 0,128, 8,8, 6) #敵が生きてる間のアニメーション
            elif c.isAvailable == False:
                c.framecount += 0.1
                if c.framecount <= 2:
                    pyxel.text(Player.x+18, Player.y - 5 - round(c.framecount)*2, '+' + str(Game.ENEMYPOINTS), 7)

#==========　プレイヤーの攻撃クラス ==========#
class Katana:
    def slice():
        for e in enemies: #mituruの攻撃
            if Player.x + 12 <= e.x <= Player.x+40 and Player.y - 8 <= e.y <= Player.y+8+16 and e.isAlive == True:
                e.isAlive = False
                Player.score += Game.ENEMYPOINTS
                Player.checkScore()
                pyxel.play(3,7)

class Gun:
    ammo = 6
    isReloading = False
    reloadcount = 0
    
    def __init__(self):
        self.x = Player.x + 15
        self.y = Player.y + 6 + random.randint(0,2)
        Gun.ammo -= 1

    def update():
        for i in bullets:
            i.x += 4

            if i.x > 208:
                bullets.remove(i)

            else:
                for e in enemies:
                    if e.x <= i.x+4 <= e.x+8 and e.y-4 <= i.y <= e.y+8 and e.isAlive: 
                        e.isAlive = False
                        bullets.remove(i) #リストから消すことで、ゲームを重くしないような工夫がされてます。
                        Player.score += Game.ENEMYPOINTS
                        Player.checkScore()
                        pyxel.play(3,7)


                for b in buildings:
                    if b.x <= i.x+4 <= b.x+16 and b.y <= i.y <= b.y+80:
                        bullets.remove(i)
        if Gun.ammo == 6:
            Gun.isReloading = False
            Gun.reloadcount = 0

        elif Gun.ammo == 0 or Gun.isReloading == True:
            Gun.isReloading = True
            Gun.reloadcount += 1
            if Gun.reloadcount % 15 == 0: #リロードカウントはpyxel.framecountみたいなもので、リロードの速度を設定するように使ってます。
                Gun.ammo += 1
                pyxel.play(0,4)


    def draw():
        for i in bullets:
            pyxel.blt(i.x,i.y, 0, 0,136, 5,2, 6)

class Wand:
    isRecharging = False
    rechargecount = 10
    charge = 46

    def __init__(self, enemyX, enemyY):
        self.x = enemyX - 4
        self.y = enemyY - 4
        self.framecount = 0
    
    def set():
        Wand.isRecharging = True
        Wand.charge =0

        for e in enemies:
            if Player.x+16 <= e.x <= 208 and e.isAlive: #画面に表示されている敵全てに対して発動します。
                emeralds.append(Wand(e.x, e.y))
                e.isAlive = False #敵が死ぬコマンドです。
                Player.score += Game.ENEMYPOINTS
                Player.checkScore()
                pyxel.play(1,3)


    def update():
        for i in emeralds:
            i.x -= 2 * Game.SPEED
            if i.x < -16:
                emeralds.remove(i)
        
        if Wand.charge == 46 and Wand.isRecharging == True:
            Wand.rechargecount = 0
            Wand.isRecharging = False
        elif Wand.isRecharging: 
            Wand.rechargecount += 2
            if Wand.rechargecount % 5 == 0:
                Wand.charge += 2

    def draw():
        for i in emeralds:
            if round(i.framecount) <= 4:
                pyxel.blt(i.x,i.y, 0, round(i.framecount)*16,144, 16,16, 6 )
                i.framecount += 0.2
            else:
                pyxel.blt(i.x,i.y, 0, 64,144, 16,16, 6)

#==========　ＵＩまとめ ==========#
class Button: #ボタン全てに対して使われているプレス関数を保存しているボタンクラスです。
    def press(x,y,w,h, u, key, forVisual): #ボタンの位置と、pyxresに保存されているボタンの位置を合わせて作られています。 forVisualは、見ためか、実際にコードを起動するかの場合わけして違いに使われています。
            if x <= pyxel.mouse_x <= x+w and y <= pyxel.mouse_y <= y+h and pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) or x <= pyxel.mouse_x <= x+w and y <= pyxel.mouse_y <= y+h and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) and forVisual == True or pyxel.btnr(key) or pyxel.btn(key) and forVisual == True:
                if forVisual:
                    return u + w
                else:
                    return True
            else:
                if forVisual:
                    return u
                else:
                    return False

class GUI:
    def inGame():
        #下のUI
        pyxel.rect(0,127, 208,17, 1)
        pyxel.line(0,126, 208,126, 7)

        pyxel.rect(0,0, 208,17, 1)
        pyxel.line(0,17, 208,17, 7)
        
        pyxel.blt(80, 128, 2, 80 if Player.canBoost else 48, 192, 16,16, 6)
        pyxel.blt(1, 128, 2, 48, 208+Player.CHARACTER*16, 16,16, 6) #キャラ画像

        pyxel.blt(144, 127, 2, 0, 176, 32, 16, 6)
        pyxel.blt(176, 127, 2, 0, 192, 32, 16, 6)

        if Player.CHARACTER == 0:
            pyxel.blt(17,128,0,48,176, 48,16, 6)
        elif Player.CHARACTER == 1:
            for i in range(Gun.ammo):
                pyxel.blt(20 + i * 7, 128, 0, 8 if Gun.isReloading else 0,176, 6,15, 6)
        elif Player.CHARACTER == 2:
            pyxel.blt(17,128,0, 0,160, 48,16, 6)
            for i in range(Wand.charge):
                pyxel.blt(17, 128, 0, 48 if Wand.isRecharging else 96,160, i,16, 6)
        
        pyxel.text(2,3, 'LEVEL:' + str(Game.level), 7) #レベル情報
        pyxel.text(2,10, 'SCORE:' + str(Player.score), 7) #スコア情報

class StartScreen:
    framecount = 0
    buttonPressed = False

    def update():
        if Button.press(72,92,64,16, 32, pyxel.KEY_P, False):
            Game.isSelecting = True
            pyxel.play(0,9)
        if Button.press(72,108,64,16, 32, pyxel.KEY_Q, False):
            pyxel.play(0,10)
            quit()
    
    def draw():
        pyxel.blt(58,10, 2, 0,144, 96,32, 6)

        pyxel.blt(72,50, 2, 0, 176, 32, 16, 6)
        pyxel.blt(104,50, 2, 0, 192, 32, 16, 6)

        pyxel.text(66,136, 'CREATED BY TADE.K', 7)
        pyxel.blt(72,92, 2, Button.press(72,92,64,16, 32, pyxel.KEY_P, True),48, 64,16, 6)
        pyxel.blt(72,108, 2, Button.press(72,108,64,16, 32, pyxel.KEY_Q, True),64, 64,16, 6)

class SelectScreen:
    def update():
        if Button.press(2,2,16,16, 0, pyxel.KEY_Q, False):
            Game.isSelecting = False
            pyxel.play(0,10)
        if Button.press(72,119,64,24, 32, pyxel.KEY_P, False):
            Game.isSelecting = False
            Game.isPlaying = True
            pyxel.play(0,9)

        if Button.press(40,60,16,24, 32, pyxel.KEY_LEFT, False):
            if Player.CHARACTER != 0:
                Player.CHARACTER -= 1
            else:
                Player.CHARACTER = 2
            pyxel.play(0,12)
        if Button.press(152,60,16,24, 64, pyxel.KEY_RIGHT, False):
            if Player.CHARACTER != 2:
                Player.CHARACTER += 1
            else:
                Player.CHARACTER = 0
            pyxel.play(0,12)
    def draw():
        pyxel.rect(0,0, 208,17, 1)
        pyxel.line(0,17, 208,17, 7)
        pyxel.blt(40,0, 2, 32,128, 128,16, 6)

        pyxel.rect(0,119, 208,25, 1)
        pyxel.blt(72,119, 2, Button.press(72,119,64,24, 32, pyxel.KEY_P, True),80, 64,24, 6)
        pyxel.line(0,118, 208,118, 7)


        pyxel.blt(2,0, 2, Button.press(2,0,16,16, 0, pyxel.KEY_Q, True),112, 16,16, 6)

        pyxel.blt(40,60, 2, Button.press(40,60,16,24, 32, pyxel.KEY_LEFT, True),104, 16,24, 6)
        pyxel.blt(152,60, 2, Button.press(152,60,16,24, 64, pyxel.KEY_RIGHT, True),104, 16,24, 6)

        pyxel.blt(-40,36, 2, 192,64+64*(Player.CHARACTER-1) if Player.CHARACTER != 0 else 192, 64,64, 6)
        pyxel.blt(184,36, 2, 192,64+64*(Player.CHARACTER+1) if Player.CHARACTER != 2 else 64, 64,64, 6)

        pyxel.blt(72,28, 2, 192,64 + 64*Player.CHARACTER, 64,64, 6)
        pyxel.rect(76,94, 56,20, 7)
        pyxel.rect(78,96, 52,16, 1)
        pyxel.blt(80,96, 2, 0,208 + 16*Player.CHARACTER, 48,16, 6)

        pyxel.blt(144, 127, 2, 0, 176, 32, 16, 6)
        pyxel.blt(176, 127, 2, 0, 192, 32, 16, 6)

class Background:
    framecount = 0
    def update():
        Background.framecount += 1
        if Background.framecount * 0.2 == 256:
            Background.framecount = 0

    def draw():
        # 背景を動かす # (背景をアセットから読み込み、pyxel.frame_countを使用して、少しずつ動かし、ある一定値を超えるとx座標をリセット)
        pyxel.rect(0,112, 208,32, 12)
        pyxel.blt(0 - Background.framecount*0.2 % 256,64, 2, 0,0, 256,48, 6)
        pyxel.blt(256 - Background.framecount*0.2 % 256 ,64, 2, 0,0, 256,48, 6)

class GameOverCard:
    def update():
        if Button.press(120,94,16,16, 0, pyxel.KEY_P, False):
            Game.reset()
            Game.isOver = False
            pyxel.play(0,9)
        elif Button.press(96,94,16,16, 0, pyxel.KEY_C, False):
            Game.reset()
            Game.isOver = False
            Game.isPlaying = False
            Game.isSelecting = True
            pyxel.play(0,11)
        elif Button.press(72,94,16,16, 0, pyxel.KEY_Q, False):
            Game.reset()
            Game.isOver = False
            Game.isPlaying = False
            Game.isSelecting = False
            pyxel.play(0,10)


    def draw():
        pyxel.rectb(47,31, 114,82, 7)
        pyxel.rect(48,32, 112,80, 1)

        pyxel.blt(72,36, 2, 96,104, 64, 24, 6)
        pyxel.line(72,60, 136,60, 7)

        pyxel.text(74,64, "HIGHSCORE:" + str(Game.HIGHSCORE), 7)
        pyxel.text(74,74, "LEVEL:" + str(Game.level), 7)
        pyxel.text(74,84, "SCORE:" + str(Player.score), 7)

        pyxel.blt(120,94, 2, Button.press(120,94,16,16, 0, pyxel.KEY_P, True),96, 16,16, 6)
        pyxel.blt(96,94, 2, Button.press(96,94,16,16, 0, pyxel.KEY_C, True),128, 16,16, 6)
        pyxel.blt(72,94, 2, Button.press(72,94,16,16, 0, pyxel.KEY_Q, True),112, 16,16, 6)

#========== LIST ==========#
buildings = [] #建物のインスタンスのデータをリストに保存
enemies = [] #敵のインスタンスのデータをリストに保存
bullets = [] #銃弾のインスタンスを足したり消したりするために、リスト化、インスタンスを消すのは難しいので、リストを使います。
emeralds = []
chips = []

for i in range(6): # range(x) x リストの中に作る建物のインスタンスの数の設定
    buildings.append(Building(i))
    enemies.append(Enemy())
    chips.append(Chip())
#========== APP CLASS ==========#
class App:
    #========== SOUND/AUDIO ==========#
    #取り損ねた音なので、低めの音を選びました。

    #========== メソッド ===========# 
    def __init__(self):
        pyxel.init(208,144, title="DASH FIGHTERS", fps=60) # Pyxel 画面のサイズとフレームレートの設定と #
        pyxel.load("Assets.pyxres") # アセットの読み込み
        pyxel.run(self.update, self.draw) # アップデートとドローの繰り返し

    def update(self):
        if Game.isPlaying and Game.isOver == False:
            Background.update()
            Building.update()
            Enemy.update()
            Player.update()
            Chip.update()
        elif Game.isPlaying == False and Game.isSelecting == False:
            Background.update()
            StartScreen.update()
        elif Game.isSelecting == True:
            Background.update()
            SelectScreen.update()
        elif Game.isOver:
            GameOverCard.update()

    def draw(self):
        if Game.isPlaying and Game.isSelecting == False:
            pyxel.mouse(False)
            pyxel.cls(6) # 背景塗りつぶし #
            Background.draw()            
            Building.draw()
            Player.draw()
            Chip.draw()
            Enemy.draw()
            GUI.inGame()            
        elif Game.isPlaying == False and Game.isSelecting == False:
            pyxel.cls(6) # 背景塗りつぶし #  
            Background.draw()            
            pyxel.mouse(True)
            StartScreen.draw()
        elif Game.isSelecting == True:
            pyxel.cls(6) # 背景塗りつぶし #     
            Background.draw()            
            SelectScreen.draw()

        if Game.isOver and (Player.isGrounded == True or Player.y > 144) :
            pyxel.mouse(True)
            GameOverCard.draw()
        
App()
