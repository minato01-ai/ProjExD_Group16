import pygame
import random
import sys
import math
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# ==========================================
# 1. 初期設定 & オーディオ初期化
# ==========================================
pygame.init()
try:
    # 音のサンプリングレートやバッファを指定して確実に初期化
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
except Exception as e:
    print(f"ミキサー初期化エラー: {e}")

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ポップカルチャー タイピングバトル ★サウンド対応版")
clock = pygame.time.Clock()

CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2
SPAWN_RADIUS = 480

# 色の定義
LOCKED_COLOR = (255, 255, 0)
ENEMY_COLOR = (255, 75, 75)
TEXT_TYPED = (100, 100, 100)
UI_COLOR = (220, 220, 220)
TEXT_JA_COLOR = (255, 255, 255)

FIRE_CORE = (255, 255, 200)   
FIRE_INNER = (255, 120, 0)    
FIRE_OUTER = (255, 40, 0)     

GRAY_CORE = (240, 240, 240)   
GRAY_INNER = (160, 160, 160)  
GRAY_OUTER = (90, 90, 90)     

if sys.platform == "win32":
    font_ja = pygame.font.SysFont("msgothic", 24)      
    font_word = pygame.font.SysFont("msgothic", 28)    
else:
    font_ja = pygame.font.SysFont("ヒラギノ角ゴpro", 22) 
    font_word = pygame.font.SysFont("ヒラギノ角ゴpro", 26)

font_ui = pygame.font.Font(None, 40)
font_title = pygame.font.Font(None, 80)

FALLBACK_COLORS = [
    (255, 100, 100), (100, 150, 255), (180, 100, 50), (100, 220, 100), (255, 150, 200)
]

def load_img(filename, w, h, fallback_color_idx):
    try:
        # ex5フォルダから見た「ゲーム」フォルダ内のパスに修正
        actual_path = os.path.join("ゲーム", filename)
        img = pygame.image.load(actual_path).convert_alpha()
        return pygame.transform.scale(img, (w, h))
    except:
        surf = pygame.Surface((w, h)).convert_alpha()
        surf.fill((0, 0, 0, 0)) 
        pygame.draw.circle(surf, FALLBACK_COLORS[fallback_color_idx], (w//2, h//2), w//2)
        return surf

# ==========================================
# 🎵 サウンドファイルの読み込み & 音量調整
# ==========================================
def load_sound(filename):
    # ex5フォルダから見た「ゲーム」フォルダ内のパスに修正
    actual_path = os.path.join("ゲーム", filename)
    if os.path.exists(actual_path):
        try:
            return pygame.mixer.Sound(actual_path)
        except Exception as e:
            print(f"音声ファイルの読み込みエラー ({filename}): {e}")
    return None

def play_bgm(filename):
    # ex5フォルダから見た「ゲーム」フォルダ内のパスに修正
    actual_path = os.path.join("ゲーム", filename)
    if os.path.exists(actual_path):
        try:
            pygame.mixer.music.load(actual_path)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.7) # BGMをしっかり聞こえるように大きく
        except Exception as e:
            print(f"BGM再生エラー: {e}")

# 全て「ゲーム」フォルダ内から読み込むように内部で自動補正されます
snd_type = load_sound("type.wav")       
snd_kill = load_sound("kill.wav")       
snd_damage = load_sound("damage.wav")   
snd_gameover = load_sound("gameover.wav")

# ★効果音の個別の音量を設定（0.0 が無音、1.0 が最大）
if snd_kill: snd_kill.set_volume(0.15)        # ★敵が倒れる音をさらに小さく調整
if snd_gameover: snd_gameover.set_volume(0.3) # ゲームオーバー音を小さく調整
if snd_type: snd_type.set_volume(1.0)         # キー入力音
if snd_damage: snd_damage.set_volume(1.0)     # ダメージ音

play_bgm("bgm.mp3")

# ==========================================
# 2. 画像と敵のデータ定義（ポップカルチャー・完全一致版）
# ==========================================
bg_images = [
    load_img("bg1.png", SCREEN_WIDTH, SCREEN_HEIGHT, 0),
    load_img("bg2.png", SCREEN_WIDTH, SCREEN_HEIGHT, 0)
]
bg_frame_count = 0

player_image = load_img("player.png", 40, 40, 0)

enemy_images = [
    load_img("enemy1.png", 40, 40, 0),
    load_img("enemy2.png", 60, 60, 1),
    load_img("enemy3.png", 60, 60, 2),
    load_img("enemy4.png", 60, 60, 3),
    load_img("enemy5.png", 60, 60, 4)
]

ENEMY_TYPES = [
    # 種類 0: 【短め】3〜5文字
    [
        {"ja": "すたんど", "en": "SUTANDO"},{"ja": "はもん", "en": "HAMON"},
        {"ja": "ふぉーす", "en": "FOOSU"},{"ja": "じぇだい", "en": "JEDAI"},
        {"ja": "しす", "en": "SISU"},{"ja": "らいとせーばー", "en": "RAITOSEEBAA"},
        {"ja": "ひーろー", "en": "HIIROO"},{"ja": "かいじん", "en": "KAIZIN"},
        {"ja": "さいたま", "en": "SAITAMA"},{"ja": "じぇのす", "en": "JENOSU"},
        {"ja": "いかげーむ", "en": "IKAGEEMU"},{"ja": "だるまさん", "en": "DARUMASAN"},
        {"ja": "かたぬき", "en": "KATANUKI"},{"ja": "ぎふん", "en": "GIHUN"},
        {"ja": "ふろんとまん", "en": "HURONTOMAN"},{"ja": "いしかめん", "en": "ISIKAMEN"},
        {"ja": "ていこく", "en": "TEIKOKU"},{"ja": "ですすたー", "en": "DESUSUTAA"},
        {"ja": "わんぱん", "en": "WANPAN"},{"ja": "ますく", "en": "MASUKU"}
    ],
    # 種類 1: 【標準】5〜8文字
    [
        {"ja": "しびれる", "en": "SIBIRERU"},{"ja": "あこがれる", "en": "AKOGARERU"},
        {"ja": "くろいせいし", "en": "KUROISEISI"}, {"ja": "あります", "en": "ARIMASU"},
        {"ja": "いやなよかん", "en": "IYANAYOKAN"},{"ja": "ふつうのぱんち", "en": "HUTUUNOPANTI"},
        {"ja": "れんぞく", "en": "RENZOKU"},{"ja": "まじなぐり", "en": "MAZINAGURI"},
        {"ja": "むきゅう", "en": "MUKYUU"},{"ja": "ぶいあいぴー", "en": "BUIAIPII"},
        {"ja": "つなひき", "en": "TUNAHIKI"},{"ja": "びーだま", "en": "BIIDAMA"},
        {"ja": "がらすのはし", "en": "GARASUNOHASI"},{"ja": "ごーるど", "en": "GOORUDO"},
        {"ja": "すたーぷらちな", "en": "SUTAAPURATINA"},{"ja": "ざわーるど", "en": "ZAWAARUDO"},
        {"ja": "だーすべいだー", "en": "DAASUBEIDAA"},{"ja": "とるーぱー", "en": "TORUUPAA"},
        {"ja": "たつまき", "en": "TATUMAKI"}, {"ja": "きんぐえんじん", "en": "KINGUENZIN"},{"ja": "もうちがう", "en": "MOUTIGAU"}
        
    ],
    # 種類 2: 【中目】6〜10文字
    [
        {"ja": "おまえは", "en": "OMAEHA"},{"ja": "ぱんのまいすう", "en": "PANNOMAISUU"},
        {"ja": "むだむだむだむだ", "en": "MUDAMUDAMUDAMUDA"},{"ja": "おらおらおらおら", "en": "ORAORAORAORA"},
        {"ja": "だがことわる", "en": "DAGAKOTOWARU"},{"ja": "しんせかい", "en": "SINSEKAI"},
        {"ja": "くずが", "en": "KUZUGA"},{"ja": "あっとうてき", "en": "ATTOUTEKI"},
        {"ja": "きんきんにひえて", "en": "KINKINNIHIETE"},{"ja": "はいぼくしゃ", "en": "HAIBOKUSYA"},
        {"ja": "ごみのようだ", "en": "GOMINOYOUDA"},{"ja": "ばるす", "en": "BARUSU"},
        {"ja": "じぇだいのきかん", "en": "JEDAINOKIKAN"},{"ja": "くろーんうぉーず", "en": "KUROONWOOZU"},
        {"ja": "ふるこん", "en": "HURUKON"},{"ja": "むめんらいだー", "en": "MUMENRAIDAA"},
        {"ja": "じてんしゃ", "en": "ZITENSYA"},{"ja": "しんかいおう", "en": "SINKAIOU"},
        {"ja": "ぼろす", "en": "BOROSU"},{"ja": "めぐみん", "en": "MEGUMIN"},
        {"ja": "西国分寺のトイレ", "en": "NISIKOKUBUNNZINOTOIRE"}
    ],
    # 種類 3: 【長め】9〜14文字
    [
        {"ja": "あっとうてきなぱわー", "en": "ATTOUTEKINAPAWAA"},{"ja": "しゅみでひーろー", "en": "SYUMIDEHIIROO"},
        {"ja": "まためろ", "en": "MATAMERO"},{"ja": "うでたてふせ", "en": "UDETATEHUSE"},
        {"ja": "じょうたいおこし", "en": "JOUTAIOKOSI"},{"ja": "すくわっと", "en": "SUKUWATTO"},
        {"ja": "らんにんぐ", "en": "RANNINGU"},{"ja": "まいにちやる", "en": "MAINITIYARU"},
        {"ja": "はげまんと", "en": "HAGEMANTO"},{"ja": "おんそくのそにっく", "en": "ONSOKUNOSONIKKU"},
        {"ja": "じごくのふぶき", "en": "ZIGOKUNOHUBUKI"},{"ja": "ぼろすかんたい", "en": "BOROSUKANTAI"},
        {"ja": "ほうこうほう", "en": "HOUKOUHOU"}, {"ja": "よんひゃく", "en": "YONHYAKU"},
        {"ja": "おおがねもち", "en": "OOGANEMOTI"},{"ja": "ですげーむ", "en": "DESUGEEMU"},
        {"ja": "しゃさつ", "en": "SYASATU"},{"ja": "おくうぉん", "en": "OKUWON"},
        {"ja": "めぐみ", "en": "MEGUMI"}, {"ja": "かなしきかこ", "en": "KANASIKIKAKO"}
    ],
    # 種類 4: 【最長・ボス級】11〜16文字
    [
        {"ja": "ひんじゃくひんじゃく", "en": "HINJAKUHINJAKU"},{"ja": "しんでいる", "en": "SINDEIRU"},
        {"ja": "つぎのせりふは", "en": "TUGINOSERIHU"},{"ja": "さいこうにははい", "en": "SAIKOUNIHAI"},
        {"ja": "すかいうぉーかー", "en": "SUKAIWOOKAA"},{"ja": "ちちおや", "en": "TITIOYA"},
        {"ja": "おまえのちちおや", "en": "OMAENOTITIOYA"},{"ja": "だーくさいど", "en": "DAAKUSAIDO"},
        {"ja": "ぎんがけい", "en": "GINGAKEI"},{"ja": "おわっちまった", "en": "OWATTIMATTA"},
        {"ja": "つよくなりすぎてしまった", "en": "TUYOKUNARISUGITESIMATTA"},{"ja": "きょうかい", "en": "KYOUKAI"},
        {"ja": "かいじんきょうかい", "en": "KAIZINKYOUKAI"},{"ja": "しゅじんこう", "en": "SYUZINKOU"},
        {"ja": "げーむをさせてくれ", "en": "GEEMUWOSASETEKURE"},{"ja": "おまえはただのうまだ", "en": "OMAEHATADANOUMADA"},
        {"ja": "スイパラいこ", "en": "SUIPARAIKO"}, {"ja": "けもの", "en": "KEMONO"},{"ja": "はやしれいな", "en": "HAYASIREINA"},
        {"ja": "けもの", "en": "KEMONO"},{"ja": "はやしれいな", "en": "HAYASIREINA"},
        {"ja": "ささもとあきら", "en": "SASAMOTOAKIRA"},{"ja": "あまりろり", "en": "AMARIRORI"},
    ]
]

# ==========================================
# 3. エフェクトクラス
# ==========================================
class FireBolt:
    def __init__(self, start_pos, target_enemy):
        self.start_x, self.start_y = start_pos
        self.target = target_enemy
        self.alive = True
        self.base_radius = 16 
        self.progress = 0.0
        self.speed = 0.025 
        self.max_height = 120 

    def update(self):
        try: target_x, target_y = self.target["x"], self.target["y"]
        except: self.alive = False; return self.alive

        self.progress += self.speed
        if self.progress >= 1.0:
            self.progress = 1.0; self.alive = False
            global particles
            particles.extend([Particle(target_x, target_y, random.choice([FIRE_INNER, FIRE_OUTER])) for _ in range(10)])

        self.shadow_x = self.start_x + (target_x - self.start_x) * self.progress
        self.shadow_y = self.start_y + (target_y - self.start_y) * self.progress
        self.height = 4 * self.max_height * self.progress * (1.0 - self.progress)
        self.draw_x = self.shadow_x; self.draw_y = self.shadow_y - self.height

        if random.random() < 0.6:
            p = Particle(self.draw_x, self.draw_y + random.randint(-3, 3), random.choice([FIRE_INNER, FIRE_OUTER]))
            p.vx, p.vy = random.uniform(-1, 1), random.uniform(0, 1.5)
            p.duration = random.randint(10, 18)
            particles.append(p)
        return self.alive

    def draw_deformed_flame(self, surface, center_x, center_y, radius, color, alpha, num_points=8):
        points = []
        for i in range(num_points):
            angle = (2 * math.pi / num_points) * i
            points.append((center_x + radius * random.uniform(0.6, 1.4) * math.cos(angle), center_y + radius * random.uniform(0.6, 1.4) * math.sin(angle)))
        flame_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        local_points = [(p[0] - center_x + radius * 2, p[1] - center_y + radius * 2) for p in points]
        if len(local_points) >= 3:
            pygame.draw.polygon(flame_surf, (*color, alpha), local_points)
            surface.blit(flame_surf, (int(center_x) - radius * 2, int(center_y) - radius * 2))

    def draw(self, surface, offset_x, offset_y):
        shadow_r = max(4, int(self.base_radius * (1.0 - (self.height / self.max_height) * 0.5)))
        shadow_surf = pygame.Surface((shadow_r*2, shadow_r*2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 80), (shadow_r, shadow_r), shadow_r)
        surface.blit(shadow_surf, (int(self.shadow_x) - shadow_r + offset_x, int(self.shadow_y) - shadow_r + offset_y))

        fx, fy = self.draw_x + offset_x, self.draw_y + offset_y
        self.draw_deformed_flame(surface, fx, fy, self.base_radius * 1.5, FIRE_OUTER, 100, 10)
        self.draw_deformed_flame(surface, fx, fy, self.base_radius * 0.9, FIRE_INNER, 180, 8)
        self.draw_deformed_flame(surface, fx, fy, self.base_radius * 0.4, FIRE_CORE, 255, 6)

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        angle, speed = random.uniform(0, 2 * math.pi), random.uniform(2, 6)
        self.vx, self.vy = speed * math.cos(angle), speed * math.sin(angle)
        self.radius = random.randint(3, 6)
        self.color = color
        self.duration = random.randint(15, 30)

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vx *= 0.94; self.vy *= 0.94
        self.radius *= 0.93; self.duration -= 1
        return self.duration > 0

    def draw(self, surface, offset_x, offset_y):
        if self.duration > 0 and self.radius > 0.1:
            p_surf = pygame.Surface((int(self.radius*2), int(self.radius*2)), pygame.SRCALPHA)
            alpha = max(0, min(255, int(self.duration * (255 / 30))))
            pygame.draw.circle(p_surf, (*self.color, alpha), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(p_surf, (int(self.x) - self.radius + offset_x, int(self.y) - self.radius + offset_y))

class GrayDebris:
    def __init__(self, x, y):
        self.x, self.y = x, y
        angle, speed = random.uniform(0, 2 * math.pi), random.uniform(4, 9)
        self.vx, self.vy = speed * math.cos(angle), speed * math.sin(angle)
        self.gravity = 0.25; self.size = random.randint(8, 16); self.duration = random.randint(25, 45)

    def update(self):
        self.x += self.vx; self.y += self.vy; self.vy += self.gravity; self.duration -= 1
        return self.duration > 0

    def draw(self, surface, offset_x, offset_y):
        if self.duration > 0:
            cs = max(1, int(self.size * (self.duration / 45)))
            debris_surf = pygame.Surface((cs*2, cs*2), pygame.SRCALPHA)
            color = GRAY_INNER if self.duration > 20 else GRAY_OUTER
            alpha = max(0, min(255, int(self.duration * (255 / 45))))
            pygame.draw.rect(debris_surf, (*color, alpha), (0, 0, cs*2, cs*2))
            surface.blit(debris_surf, (int(self.x) - cs + offset_x, int(self.y) - cs + offset_y))

# ==========================================
# 4. ゲーム変数初期化
# ==========================================
enemies = []
locked_enemy = None
score = 0
hp = 5
game_state = "PLAYING"
spawn_timer = 0
spawn_rate = 180 

combo_count = 0      
shake_frames = 0     
fire_bolts = []      
particles = []       
gray_debris = []     

def create_enemy():
    angle = random.uniform(0, 2 * math.pi)
    x = CENTER_X + SPAWN_RADIUS * math.cos(angle)
    y = CENTER_Y + SPAWN_RADIUS * math.sin(angle)
    
    enemy_type_idx = random.randint(0, 4)
    word_data = random.choice(ENEMY_TYPES[enemy_type_idx])
    chosen_image = enemy_images[enemy_type_idx]
    
    move_dir = math.atan2(CENTER_Y - y, CENTER_X - x)
    rot_angle = -math.degrees(move_dir) + 90 if enemy_type_idx == 0 else 0
    offset_ja = -65 if enemy_type_idx == 0 else -85
    offset_en = -40 if enemy_type_idx == 0 else -60
    
    return {
        "x": x, "y": y, "move_dir": move_dir,  
        "word_ja": word_data["ja"], "word_en": word_data["en"], "index": 0,
        "speed": random.uniform(0.5, 1.0) + (score // 1000) * 0.1,
        "image": chosen_image, "rot_angle": rot_angle, "offset_ja": offset_ja, "offset_en": offset_en
    }

enemies.append(create_enemy())

# ==========================================
# 5. メインループ
# ==========================================
running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and game_state == "PLAYING":
            pressed_key = event.unicode.upper()
            if len(pressed_key) != 1 or not pressed_key.isalpha(): continue
            
            matched = False
            if locked_enemy is None:
                for e in enemies:
                    if e["word_en"][e["index"]] == pressed_key:
                        locked_enemy = e
                        e["index"] += 1
                        matched = True
                        fire_bolts.append(FireBolt((CENTER_X, CENTER_Y), e))
                        if snd_type: snd_type.play()
                        break
                if not matched: combo_count = 0
            else:
                if locked_enemy["word_en"][locked_enemy["index"]] == pressed_key:
                    locked_enemy["index"] += 1
                    fire_bolts.append(FireBolt((CENTER_X, CENTER_Y), locked_enemy))
                    if snd_type: snd_type.play()
                    matched = True
                else:
                    combo_count = 0
            
            if locked_enemy and locked_enemy["index"] >= len(locked_enemy["word_en"]):
                if snd_kill: snd_kill.play()
                
                particles.extend([Particle(locked_enemy["x"], locked_enemy["y"], random.choice([GRAY_INNER, GRAY_OUTER])) for _ in range(75)])
                gray_debris.extend([GrayDebris(locked_enemy["x"], locked_enemy["y"]) for _ in range(15)])
                
                shake_frames = 15 
                combo_count += 1
                score += 100 * combo_count
                    
                enemies.remove(locked_enemy)
                locked_enemy = None
                
        elif event.type == pygame.KEYDOWN and game_state == "GAMEOVER":
            if event.key == pygame.K_SPACE:
                enemies.clear(); fire_bolts.clear(); particles.clear(); gray_debris.clear()
                locked_enemy = None
                score = 0; hp = 5; spawn_rate = 180; spawn_timer = 0; combo_count = 0
                enemies.append(create_enemy())
                game_state = "PLAYING"
                play_bgm("bgm.mp3")

    if game_state == "PLAYING":
        spawn_timer += 1
        if spawn_timer >= spawn_rate:
            enemies.append(create_enemy())
            spawn_timer = 0
            spawn_rate = max(70, 180 - (score // 1000) * 15)

        bg_frame_count += 1

        fire_bolts = [b for b in fire_bolts if b.update()]
        particles = [p for p in particles if p.update()]
        gray_debris = [d for d in gray_debris if d.update()]

        for e in enemies[:]:
            e["x"] += e["speed"] * math.cos(e["move_dir"])
            e["y"] += e["speed"] * math.sin(e["move_dir"])
            
            distance = math.hypot(e["x"] - CENTER_X, e["y"] - CENTER_Y)
            if distance < 25:
                if snd_damage: snd_damage.play()
                
                if e == locked_enemy: locked_enemy = None
                enemies.remove(e)
                combo_count = 0
                shake_frames = 20
                hp -= 1
                if hp <= 0: 
                    game_state = "GAMEOVER"
                    pygame.mixer.music.stop()
                    if snd_gameover: snd_gameover.play()

    offset_x, offset_y = 0, 0
    if shake_frames > 0:
        intensity = 15 
        offset_x, offset_y = random.randint(-intensity, intensity), random.randint(-intensity, intensity)
        shake_frames -= 1

    current_bg_idx = (bg_frame_count // 30) % len(bg_images)
    screen.blit(bg_images[current_bg_idx], (offset_x, offset_y))
    screen.blit(player_image, (CENTER_X - 20 + offset_x, CENTER_Y - 20 + offset_y))
    
    for b in fire_bolts: b.draw(screen, offset_x, offset_y)
    for p in particles: p.draw(screen, offset_x, offset_y)
    for d in gray_debris: d.draw(screen, offset_x, offset_y) 

    for e in enemies:
        rotated_enemy_img = pygame.transform.rotate(e["image"], e["rot_angle"])
        new_rect = rotated_enemy_img.get_rect(center=(int(e["x"]), int(e["y"])))
        screen.blit(rotated_enemy_img, (new_rect.x + offset_x, new_rect.y + offset_y))

        surf_ja = font_ja.render(e["word_ja"], True, TEXT_JA_COLOR)
        color_en = LOCKED_COLOR if e == locked_enemy else ENEMY_COLOR
        typed_part, untyped_part = e["word_en"][:e["index"]], e["word_en"][e["index"]:]
        surf_typed = font_word.render(typed_part, True, TEXT_TYPED)
        surf_untyped = font_word.render(untyped_part, True, color_en)
        total_en_width = surf_typed.get_width() + surf_untyped.get_width()
        
        screen.blit(surf_ja, (int(e["x"]) - surf_ja.get_width() // 2 + offset_x, int(e["y"]) + e["offset_ja"] + offset_y))
        screen.blit(surf_typed, (int(e["x"]) - total_en_width // 2 + offset_x, int(e["y"]) + e["offset_en"] + offset_y))
        screen.blit(surf_untyped, (int(e["x"]) - total_en_width // 2 + surf_typed.get_width() + offset_x, int(e["y"]) + e["offset_en"] + offset_y))

    if game_state == "PLAYING":
        screen.blit(font_ui.render(f"SCORE: {score}", True, UI_COLOR), (20, 20))
        screen.blit(font_ui.render(f"LIFE: {hp} / 5", True, UI_COLOR), (20, 60))
    elif game_state == "GAMEOVER":
        mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
        mask.fill((10, 10, 20, 200)); screen.blit(mask, (0, 0))
        screen.blit(font_title.render("GAME OVER", True, (255, 65, 65)), (CENTER_X - 180, 200))
        screen.blit(font_ui.render(f"FINAL SCORE: {score}", True, UI_COLOR), (CENTER_X - 150, 300))
        screen.blit(font_ui.render("Press SPACE to Restart", True, (0, 255, 255)), (CENTER_X - 150, 380))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()