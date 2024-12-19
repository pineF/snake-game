#!/usr/bin/env python
# coding: utf-8

# # Snake Bite
# 
# - オリジナル
#     - https://www.edureka.co/blog/snake-game-with-pygame/
# 

# In[1]:


# ライブラリのインポート
import pygame
import time
import random
import datetime
import pickle
import os
import asyncio


# In[2]:


# 各種設定
white = (255, 255, 255)
black = (0, 0, 0)
dark_green = (162, 209, 73)
light_green = (170, 215, 81)

yellow = (0, 155, 255)
red = (231, 71, 29)
green = (255, 165, 0)
blue = (79, 125, 237)

size_block = 20
num_block_width = 45
num_block_height = 30

dis_width = size_block * num_block_width
dis_height = size_block * num_block_height

snake_speed = 13


# In[3]:


# 画像の読み込み

# 矢印キー
key_image = pygame.image.load("assets/矢印キー.png")
key_image = pygame.transform.scale(key_image, (250, 150))

# 蛇のあたま
snake_head_image = pygame.image.load("assets/snake-head.png")
snake_head_image = pygame.transform.scale(snake_head_image, ((size_block*32/26)+1, (size_block*32/26)+1))

# えさ
food_image = pygame.image.load("assets/food.png")
food_image = pygame.transform.scale(food_image, (size_block, size_block))

# 障害物
wall_image = pygame.image.load("assets/poison_mushroom.png")
wall_image = pygame.transform.scale(wall_image, (size_block*11, size_block*11))


# In[4]:


# 各種関数

# スコアの表示
def show_score(dis, font, score):
    value = font.render(f"Your Score: {score}", True, white)
    dis.blit(value, [5, 0])

# 蛇の描画
def draw_snake(dis, snake_list, snake_head_image, x_change, y_change):
    for i, (x, y) in enumerate(snake_list):
        if i == len(snake_list) - 1:  # 先頭部分
            # 進行方向に応じて画像を回転
            if x_change == 1 and y_change == 0:  # 右方向
                rotated_image = pygame.transform.rotate(snake_head_image, 270)
            elif x_change == -1 and y_change == 0:  # 左方向
                rotated_image = pygame.transform.rotate(snake_head_image, 90)
            elif x_change == 0 and y_change == 1:  # 下方向
                rotated_image = pygame.transform.rotate(snake_head_image, 180)
            elif x_change == 0 and y_change == -1:  # 上方向
                rotated_image = pygame.transform.rotate(snake_head_image, 0)
            else:
                rotated_image = snake_head_image  # デフォルト

            # 画像の幅と高さを取得
            img_width, img_height = rotated_image.get_size()

            # セルの中心に配置
            dis.blit(rotated_image, (x * size_block + (size_block - img_width) / 2, 
                                     y * size_block + (size_block - img_height) / 2))

        else:
            # 体の部分は単色で描画
            pygame.draw.rect(dis, blue, [x * size_block, y * size_block, size_block, size_block])

# 餌の描画
def draw_food(dis, food_x, food_y):
    dis.blit(food_image, (food_x * size_block, food_y * size_block))


# 障害物の描画
def draw_wall(dis, walls):
    for wall_x, wall_y in walls:
        # 画像の幅と高さを取得
            img_width, img_height = wall_image.get_size()
        # セルの中心に配置
            dis.blit(wall_image, (wall_x * size_block + size_block / 2 - img_width / 2,
                                     wall_y * size_block + size_block / 2 - img_height / 2))

# 障害物の位置を決める
def make_wall(snake_list, food_x, food_y, num_walls=10):
    walls = []
    while len(walls) < num_walls:
        wall_x = random.randrange(num_block_width)
        wall_y = random.randrange(num_block_height)
        
        # 障害物が蛇の位置や餌と重ならないようにする
        if (wall_x, wall_y) != (food_x, food_y) and (wall_x, wall_y) not in snake_list:
            walls.append((wall_x, wall_y))
    return walls
        
# メッセージの表示
def message(dis, font, msg, color, width, height, image=None):
    mesg = font.render(msg, True, color)
    mesg_rect = mesg.get_rect(topleft=(width, height))  # テキストの位置を設定
    dis.blit(mesg, mesg_rect)
    
    if image:
        # 画像の幅と高さを取得
        img_width, img_height = wall_image.get_size()
        image_rect = image.get_rect(topleft=(mesg_rect.right + 15 - img_width/2, height + 10 - img_height/2))
        dis.blit(image, image_rect)

# 新しい餌の位置を決める
def make_food():
    food_x = random.randrange(num_block_width)
    food_y = random.randrange(num_block_height)
    return food_x, food_y

# 背景描画関数
def draw_background(dis):
    for row in range(num_block_height):
        for col in range(num_block_width):
            color = light_green if (row + col) % 2 == 0 else dark_green
            pygame.draw.rect(dis, color, [col * size_block, row * size_block, size_block, size_block])
            
# スコアを記録し、各モードで上位5件を保持する関数
SCORE_FILE = "score_log.pkl"

def log_score(score, mode, top_n=5):
    # スコアファイルを読み込む (ファイルがなければ空の辞書)
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "rb") as file:
            scores_by_mode = pickle.load(file)
    else:
        scores_by_mode = {}

    # モードごとのスコアを追加
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    scores_by_mode.setdefault(mode, []).append((timestamp, score))

    # 上位5件のみ保持 (スコア降順でソート)
    scores_by_mode[mode] = sorted(scores_by_mode[mode], key=lambda x: x[1], reverse=True)[:top_n]

    # 更新後のデータをpickleで保存
    with open(SCORE_FILE, "wb") as file:
        pickle.dump(scores_by_mode, file)

# 指定モードの上位スコアを取得する関数
def get_top_scores(mode, top_n=5):
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "rb") as file:
            scores_by_mode = pickle.load(file)
            # モードに該当するスコアがあればスコア部分のみを抽出
            if mode in scores_by_mode:
                scores = [score for _, score in scores_by_mode[mode]]
            else:
                scores = []
    else:
        scores = []
    
    # スコアが不足している場合 "-" で埋める
    while len(scores) < top_n:
        scores.append("-")
    
    return scores[:top_n]


# In[5]:


# 難易度設定
EASY = "easy"
MEDIUM = "medium"
HARD = "hard"

# 難易度選択画面の表示関数
def choose_difficulty():
    pygame.init()
    dis = pygame.display.set_mode((dis_width, dis_height))
    pygame.display.set_caption("Mode Selection")
    
    difficulty = None

    #### フォント設定##########################################
    font1 = pygame.font.SysFont("bahnschrift", 35, bold = True)
    font2 = pygame.font.SysFont("bahnschrift", 25)
    ###########################################################
    
    while difficulty is None:
        dis.fill(dark_green)
        
        # メッセージ表示
        message(dis, font1, "Choose Difficulty :", white, dis_width / 6, dis_height / 3 - 100)
        
        # 難易度オプションの表示
        message(dis, font1, "Press E for EASY :", green, dis_width / 4 - 20, dis_height / 3 - 50)
        message(dis, font2, "Normal snake game", green, dis_width / 4 + 10, dis_height / 3 - 15)
        message(dis, font1, "Press M for MEDIUM :", yellow, dis_width / 4 - 20, dis_height / 3 + 15)
        message(dis, font2, "If you hit poisonous mushrooms, the game is over", yellow, dis_width / 4 + 10, dis_height / 3 + 50, wall_image)
        message(dis, font1, "Press H for HARD : Brain Training!", red, dis_width / 4 - 20, dis_height / 3 + 80)
        message(dis, font2, "Moves in the opposite direction to the operation", red, dis_width / 4 + 10, dis_height / 3 + 115)
        
        # 矢印キー画像の表示
        message(dis, font1, "Controls :", white, dis_width / 6, dis_height / 3 + 180)
        
        key_rect = key_image.get_rect(center=(dis_width / 2, dis_height / 1.5 + 80))
        dis.blit(key_image, key_rect)
        
        
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    difficulty = EASY
                elif event.key == pygame.K_m:
                    difficulty = MEDIUM
                elif event.key == pygame.K_h:
                    difficulty = HARD

    return difficulty


# In[6]:


# ランキング表示＆遷移
def show_ranking_and_wait(dis, font, scores, modes, mode_names):
    """ランキングを表示し、Cキーが押されたらモード選択に戻る"""
    draw_background(dis)
    
    # モードごとのランキングを描画
    ### フォント設定 #######################################
    ranking_font = pygame.font.SysFont("rockwellextra", 30)
    ranking_font2 = pygame.font.SysFont("cooperblack", 25)
    font_msg = pygame.font.SysFont("bahnschrift", 30)
    ########################################################

    # メッセージの表示
    mesg_game_over = ranking_font.render("GAME OVER !", True, red)
    mesg_press_cq = ranking_font.render("Press C-Mode Selection, Q-Quit", True, red)
    mesg_top_score = ranking_font.render("Top 5 Score", True, white)
    dis.blit(mesg_game_over, [(dis_width - mesg_game_over.get_width()) / 2, dis_height / 3 - 60])
    dis.blit(mesg_press_cq, [(dis_width - mesg_press_cq.get_width()) / 2, dis_height / 3])
    dis.blit(mesg_top_score, [(dis_width - mesg_top_score.get_width()) / 2, dis_height / 3 + 55])

    show_score(dis, font, scores)

    column_width = dis_width // 3  # 各列の幅

    for i, mode in enumerate(modes):
        column_x = i * column_width + column_width // 6
        column_y = dis_height / 3 + 100
        dis.blit(ranking_font2.render(f"{mode_names[i]}", True, white), [column_x, column_y])

        # スコアを取得して描画
        top_scores = get_top_scores(mode)
        for j, score in enumerate(top_scores):
            score_text = ranking_font.render(f"{j+1}. {score}", True, white)
            dis.blit(score_text, [column_x, column_y + (j + 1) * 30])

    pygame.display.update()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "a"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # 終了
                    return "a"
                if event.key == pygame.K_c:  # モード選択
                    return "mode_selection"


# In[7]:


# メインループ

async def game_loop():
          
    difficulty = choose_difficulty()  # 難易度を取得
    
    if difficulty is None:
        game_init = True
        game_close = True
    
    else:
        game_init = True
        game_over = False
        game_close = False
        logged_score = False  # スコア記録フラグ
        
        # pygameの初期化
        pygame.init()
        dis = pygame.display.set_mode((dis_width, dis_height))
        pygame.display.set_caption("Snake Game by Edureka")

        clock = pygame.time.Clock()
        await asyncio.sleep(0)

        ### フォント設定 ########################################
        font_score = pygame.font.SysFont("cooperblack", 35)
        ########################################################
        
        ### 効果音の読み込み ####################################
        bite_sound = pygame.mixer.Sound("assets/bite_sound.ogg")
        gameover_sound = pygame.mixer.Sound("assets/gameover_sound.ogg")
        move_sound = pygame.mixer.Sound("assets/move_sound.ogg")
        ##########################################################
        
    while True:
        if game_init:
            # ゲームの初期化
            x = num_block_width // 2
            y = num_block_height // 2

            x_change = 0
            y_change = 0
            
            snake_list = []
            length_of_snake = 1

            food_x, food_y = make_food()
            walls = make_wall(snake_list, food_x, food_y)

            game_init = False

        elif game_close:
            # ゲーム終了

            pygame.quit()
            break

        elif game_over:
            # スコアをログに記録 (一度だけ)
            if not logged_score:
                log_score(length_of_snake - 1, difficulty)
                logged_score = True

            # ランキング表示と選択結果の処理
            modes = [EASY, MEDIUM, HARD]
            mode_names = ["EASY", "MEDIUM", "HARD"]
            result = show_ranking_and_wait(dis, font_score, length_of_snake - 1, modes, mode_names)

            if result == "mode_selection":
                difficulty = choose_difficulty()  # モード選択に戻る
                if difficulty == None:
                    game_close = True
                else:
                    game_init = True
                logged_score = False
                game_over = False
                
            elif result == "a":
                game_close = True

        else:
            # ゲーム中

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_close = True
                if event.type == pygame.KEYDOWN:
                    if difficulty == EASY: #EASYのとき
                        if event.key == pygame.K_LEFT and x_change == 0:
                            x_change = -1
                            y_change = 0
                        elif event.key == pygame.K_RIGHT and x_change == 0:
                            x_change = 1
                            y_change = 0
                        elif event.key == pygame.K_UP and y_change == 0:
                            y_change = -1
                            x_change = 0
                        elif event.key == pygame.K_DOWN and y_change == 0:
                            y_change = 1
                            x_change = 0
                        move_sound.play()
                    elif difficulty == MEDIUM: #MEDIUMのとき                 
                        if event.key == pygame.K_LEFT and x_change == 0:
                            x_change = -1
                            y_change = 0
                        elif event.key == pygame.K_RIGHT and x_change == 0:
                            x_change = 1
                            y_change = 0
                        elif event.key == pygame.K_UP and y_change == 0:
                            y_change = -1
                            x_change = 0
                        elif event.key == pygame.K_DOWN and y_change == 0:
                            y_change = 1
                            x_change = 0
                        move_sound.play()
                    else: #HARDのとき
                        if event.key == pygame.K_LEFT and x_change == 0:
                            x_change = 1
                            y_change = 0
                        elif event.key == pygame.K_RIGHT and x_change == 0:
                            x_change = -1
                            y_change = 0
                        elif event.key == pygame.K_UP and y_change == 0:
                            y_change = 1
                            x_change = 0
                        elif event.key == pygame.K_DOWN and y_change == 0:
                            y_change = -1
                            x_change = 0
                        move_sound.play()

            # 蛇の移動処理
            x += x_change
            y += y_change

            # 自分自身との当たり判定
            snake_head = (x, y)
            snake_list.append(snake_head)
            if len(snake_list) > length_of_snake:
                del snake_list[0]
            for xy in snake_list[:-1]:
                if xy == snake_head:
                    gameover_sound.play()
                    game_over = True
            
            # 壁との当たり判定
            if x >= num_block_width or x < 0 or y >= num_block_height or y < 0:
                gameover_sound.play()
                game_over = True
            
            if difficulty == MEDIUM:
                if snake_head in walls:
                    gameover_sound.play()
                    game_over = True
        
            # 餌を食べたかどうかの判定
            if x == food_x and y == food_y:
                food_x, food_y = make_food()
                length_of_snake += 1
                bite_sound.play()
                walls = make_wall(snake_list, food_x, food_y)
                

            # 描画
            draw_background(dis)
            draw_food(dis, food_x, food_y)
            if difficulty == MEDIUM:
                draw_wall(dis, walls)
            draw_snake(dis, snake_list, snake_head_image, x_change, y_change)
            show_score(dis, font_score, length_of_snake - 1)
            pygame.display.update()

            clock.tick(snake_speed)


# In[8]:


# メインループの実行
asyncio.run(game_loop())

