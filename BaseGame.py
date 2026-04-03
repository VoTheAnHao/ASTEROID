import pygame
import sys
import math
import time
import random

from Ship import Ship
from ASTROID import Asteroid
from ai_controller import AIController
from bullet import Bullet
from Score import Score
from heart import Heart
from leaderboard import Leaderboard
from boss import Boss
from sound_manager import SoundManager
from utils import resource_path

WHITE = (255, 255, 255)



class BaseGame:

    # ================= INIT =================
    def __init__(self, screen, clock, width, height):
        self.screen = screen
        self.clock = clock
        self.width = width
        self.height = height

        self.score = Score()
        self.ship = Ship(width, height)
        self.bullets = []
        self.boss = None
        self.in_boss_fight = False

        self.asteroids = []
        for _ in range(6):
            self.spawn_asteroid()

        self.ai = AIController()
        self.auto_mode = False
        self.paused = False
        self.exit_to_menu = False

        self.heart = Heart()

        self.start_time = time.time()
        self.leaderboard = Leaderboard()
        self.font_small = pygame.font.SysFont("arial", 24)

        self.sound = SoundManager()
        self.sound.play_music(self.sound.arcade_music)

        self.volume = 0.5
        self.dragging_volume = False

        # ===== POWERUP SYSTEM =====
        self.powerup = None
        self.powerup_timer = 0
        self.has_totem = False
        self.powerup_images = {
            "bomb": pygame.image.load(resource_path("asset/bomb-removebg-preview.png")),
            "medkit": pygame.image.load(resource_path("asset/medlit-removebg-preview.png")),
            "space_bomb": pygame.image.load(resource_path("asset/space bomb-removebg-preview.png")),
            "random": pygame.image.load(resource_path("asset/random-removebg-preview.png")),
            "totem": pygame.image.load(resource_path("asset/totem-removebg-preview.png"))
        }  

        for key in self.powerup_images:
            self.powerup_images[key] = pygame.transform.scale(
                self.powerup_images[key], (40, 40)
            )

        # ===== BOMB =====
        self.bomb_active = False
        self.bomb_end_time = 0
    def spawn_powerup(self):
        types = ["bomb", "medkit", "space_bomb", "random", "totem"]

        if self.has_totem:
            types.remove("totem")

        self.powerup = {
            "type": random.choice(types),
            "x": random.randint(50, self.width - 50),
            "y": random.randint(50, self.height - 50)
        }
    # ================= ASTEROID =================
    def spawn_asteroid(self):
        while True:
            a = Asteroid(self.width, self.height)
            if math.hypot(a.x - self.ship.x, a.y - self.ship.y) > 150:
                self.asteroids.append(a)
                break

    # ================= EVENTS =================
    def common_events(self):
        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_ESCAPE:
                    self.paused = not self.paused

                if e.key == pygame.K_t:
                    self.auto_mode = not self.auto_mode

                if e.key == pygame.K_SPACE:
                    self.shoot()

    # ================= SHOOT =================
    def shoot(self):
        self.sound.play_shoot()
        gun_x, gun_y = self.ship.get_gun_position()

        if self.ship.power_mode:
            for offset in [-15, 0, 15]:
                self.bullets.append(
                    Bullet(gun_x, gun_y, self.ship.angle + offset,
                           self.ship.vel_x, self.ship.vel_y)
                )
        else:
            self.bullets.append(
                Bullet(gun_x, gun_y, self.ship.angle)
            )

    # ================= UPDATE =================
    def update_entities(self):
        
        #BOSS TRIGGER
        if self.score.score >= 200 and not self.boss:
            self.boss = Boss(self.width, self.height, self.sound)
            self.in_boss_fight = True
            self.sound.play_music(self.sound.boss_music)
        # 🔥 BOSS MODE
        if self.in_boss_fight:
            self.asteroids.clear()
            return self.run_boss_mode()

        # ===== AI =====
        if self.auto_mode:
            self.ai.control(self.ship, self.asteroids, self.bullets, "arcade")

        self.ship.draw(self.screen)
        self.ship.check_power(self.score.score)

        # ===== BULLETS =====
        for b in self.bullets[:]:
            b.update()
            pygame.draw.circle(self.screen, WHITE, (int(b.x), int(b.y)), 3)
            if not self.in_boss_fight:
                if b.is_dead(self.width, self.height):
                    self.bullets.remove(b)
        # ===== ASTEROIDS =====
        for a in self.asteroids[:]:
            a.move()
            a.draw(self.screen)

            # bullet hit
            for b in self.bullets[:]:
                if math.hypot(a.x - b.x, a.y - b.y) < a.radius:
                    self.asteroids.remove(a)
                    self.bullets.remove(b)
                    self.asteroids.extend(a.split())
                    self.score.add(10)
                    break

            # ship hit
            if math.hypot(a.x - self.ship.x, a.y - self.ship.y) < a.radius + self.ship.radius:

                if self.ship.power_mode:
                    self.asteroids.remove(a)
                    self.asteroids.extend(a.split())
                    self.score.add(10)
                    continue

                if self.ship.invincible == 0:
                    self.heart.lose_life()
                    self.ship.reset_position()
                    self.ship.invincible = 120
                    break

        # ===== BOMB EFFECT =====
        if self.bomb_active:
            for a in self.asteroids[:]:
                if math.hypot(a.x - self.ship.x, a.y - self.ship.y) < 150:
                    self.asteroids.remove(a)
                    self.asteroids.extend(a.split())

            if time.time() > self.bomb_end_time:
                self.bomb_active = False

        # ===== POWERUP SPAWN =====
        if not self.powerup and time.time() > self.powerup_timer:
            self.spawn_powerup()

        # ===== POWERUP DRAW + PICK =====
        if self.powerup:
            self.draw_powerup()

            if math.hypot(self.ship.x - self.powerup["x"],
                          self.ship.y - self.powerup["y"]) < 30:

                self.apply_powerup(self.powerup["type"])

                if self.powerup["type"] == "totem":
                    self.has_totem = True

                self.powerup = None
                self.powerup_timer = time.time() + 10

        # ===== GAME OVER =====
        if self.heart.is_dead():

            # 🔮 TOTEM REVIVE
            if self.has_totem:
                self.has_totem = False
                self.heart.lives = 3
                self.ship.power_mode = True
                self.ship.invincible = 180
                return True

            return self.game_over_screen()

        # ===== DIFFICULTY =====
        target = min(6 + self.score.score // 50, 20)

        while len(self.asteroids) < target:
            self.spawn_asteroid()

        return True

    # ================= POWERUP =================
    def draw_powerup(self):
        img = self.powerup_images[self.powerup["type"]]

        rect = img.get_rect(center=(self.powerup["x"], self.powerup["y"]))
        self.screen.blit(img, rect)

    def apply_powerup(self, type):

        if type == "random":
            type = random.choice(["bomb", "medkit", "space_bomb"])

        if type == "bomb":
            self.bomb_active = True
            self.bomb_end_time = time.time() + 7

        elif type == "medkit":
            self.heart.lives += 1

        elif type == "space_bomb":
            self.asteroids.clear()

        elif type == "totem":
            pass

    # ================= UI =================
    def draw_status(self):
        status = "AUTO: ON (T)" if self.auto_mode else "AUTO: OFF (T)"
        txt = self.font_small.render(status, True, WHITE)
        self.screen.blit(txt, (10, 10))

        self.score.draw(self.screen)
        self.heart.draw(self.screen)

    # ================= PAUSE =================
    def pause_menu(self):
        font = pygame.font.SysFont("arial", 40)

        while True:
            self.screen.fill((0, 0, 0))

            # ===== TITLE =====
            title = font.render("PAUSED", True, WHITE)
            self.screen.blit(title, (self.width//2 - 80, 100))

            # ===== BUTTON =====
            cont_btn = pygame.Rect(self.width//2 - 100, 250, 200, 50)
            exit_btn = pygame.Rect(self.width//2 - 100, 320, 200, 50)

            pygame.draw.rect(self.screen, (100,100,100), cont_btn)
            pygame.draw.rect(self.screen, WHITE, cont_btn, 2)

            pygame.draw.rect(self.screen, (100,100,100), exit_btn)
            pygame.draw.rect(self.screen, WHITE, exit_btn, 2)

            self.screen.blit(font.render("CONTINUE", True, WHITE),
                            (cont_btn.centerx - 80, cont_btn.centery - 20))
            self.screen.blit(font.render("EXIT", True, WHITE),
                            (exit_btn.centerx - 40, exit_btn.centery - 20))

            # ===== 🔥 VOLUME =====
            slider = self.draw_volume_slider(self.width//2 - 100, 420)

            pygame.display.flip()

            # ===== EVENT =====
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                # ===== CLICK =====
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if cont_btn.collidepoint(e.pos):
                        self.paused = False
                        return False

                    if exit_btn.collidepoint(e.pos):
                        self.exit_to_menu = True
                        return True

                    # 🔥 volume click
                    if slider and slider.collidepoint(e.pos):
                        self.dragging_volume = True

                # ===== RELEASE =====
                if e.type == pygame.MOUSEBUTTONUP:
                    self.dragging_volume = False

                # ===== DRAG =====
                if e.type == pygame.MOUSEMOTION and self.dragging_volume:
                    x = e.pos[0]
                    rel = x - slider.x
                    self.volume = max(0, min(1, rel / slider.width))

                    self.sound.set_volume(self.volume)

    # ================= COUNTDOWN =================
    def countdown(self):
        font = pygame.font.SysFont("arial", 80)

        for i in range(3, 0, -1):
            self.screen.fill((0, 0, 0))
            txt = font.render(str(i), True, WHITE)
            self.screen.blit(txt, (self.width//2 - 20, self.height//2 - 40))
            pygame.display.flip()
            pygame.time.delay(1000)
    
    def game_over_screen(self):
        self.sound.stop_all()
        self.sound.play_gameover()
        font_big = pygame.font.SysFont("arial", 60)
        font_small = pygame.font.SysFont("arial", 30)

        input_mode = False
        player_name = ""

        while True:
            self.screen.fill((0, 0, 0))

            # TITLE
            title = font_big.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(title, (self.width//2 - 170, 100))

            # BUTTON
            exit_btn = pygame.Rect(self.width//2 - 100, 250, 200, 50)
            save_btn = pygame.Rect(self.width//2 - 100, 320, 200, 50)

            pygame.draw.rect(self.screen, (100,100,100), exit_btn)
            pygame.draw.rect(self.screen, (255,255,255), exit_btn, 2)

            pygame.draw.rect(self.screen, (100,100,100), save_btn)
            pygame.draw.rect(self.screen, (255,255,255), save_btn, 2)

            txt1 = font_small.render("EXIT", True, (255,255,255))
            txt2 = font_small.render("SAVE & EXIT", True, (255,255,255))

            self.screen.blit(txt1, (exit_btn.centerx - txt1.get_width()//2, exit_btn.centery - 12))
            self.screen.blit(txt2, (save_btn.centerx - txt2.get_width()//2, save_btn.centery - 12))

            # INPUT NAME
            if input_mode:
                box = pygame.Rect(self.width//2 - 150, 400, 300, 50)
                pygame.draw.rect(self.screen, (255,255,255), box, 2)

                name_txt = font_small.render(player_name, True, (255,255,255))
                self.screen.blit(name_txt, (box.x + 10, box.y + 10))

            pygame.display.flip()

            for e in pygame.event.get():

                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if e.type == pygame.MOUSEBUTTONDOWN:
                    if exit_btn.collidepoint(e.pos):
                        self.sound.stop_all()
                        pygame.mixer.music.stop()
                        return False

                    if save_btn.collidepoint(e.pos):
                        input_mode = True

                if e.type == pygame.KEYDOWN and input_mode:

                    if e.key == pygame.K_RETURN:
                        play_time = time.time() - self.start_time

                        self.leaderboard.save_score(
                            self.score.score,
                            play_time,
                            player_name
                        )
                        return False

                    elif e.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]

                    else:
                        player_name += e.unicode
    # ================= BOSS MODE =================
    def run_boss_mode(self):

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    self.shoot()

        self.screen.fill((0, 0, 0))

        # ===== BOX =====
        box_left = 250
        box_top = 350
        box_width = 300
        box_height = 150

        pygame.draw.rect(self.screen, WHITE,
                         (box_left, box_top, box_width, box_height), 2)

        # ===== PLAYER =====
        keys = pygame.key.get_pressed()
        self.ship.control(keys)
        self.ship.update()

        # 🔥 CLAMP
        self.ship.x = max(box_left, min(self.ship.x, box_left + box_width))
        self.ship.y = max(box_top, min(self.ship.y, box_top + box_height))

        self.ship.draw(self.screen)

        # ===== BOSS =====
        hit = self.boss.update(self.screen, self.ship)
        self.boss.draw(self.screen)
        self.boss.draw_health_bar(self.screen)

        if hit and self.ship.invincible == 0:
            self.sound.play_death()
            self.heart.lose_life()
            self.ship.invincible = 60

        # ===== BULLETS =====
        for b in self.bullets[:]:
            b.update()
            pygame.draw.circle(self.screen, WHITE, (int(b.x), int(b.y)), 3)

            # trúng boss
            if self.boss and abs(b.x - self.boss.x) < 60 and abs(b.y - self.boss.y) < 60:

                if self.boss.shield > 0:
                    self.boss.shield -= 1
                else:
                    self.boss.hp -= 5

                self.bullets.remove(b)
                continue

        # xóa đạn khi ra ngoài màn
            if not self.in_boss_fight:
                if b.is_dead(self.width, self.height):
                    self.bullets.remove(b)

        # ===== BOSS DIE =====
        if self.boss and self.boss.hp <= 0:
            self.boss = None
            self.in_boss_fight = False
            self.score.add(100)

            return self.win_screen() 

        # ===== GAME OVER =====
        if self.heart.lives <= 0:
            return self.game_over_screen()

        pygame.display.flip()
        return True

    # ================= UI =================
    def draw_status(self):
        txt = self.font_small.render(
            "AUTO: ON (T)" if self.auto_mode else "AUTO: OFF (T)", True, WHITE)
        self.screen.blit(txt, (10, 10))

        self.score.draw(self.screen)
        self.heart.draw(self.screen)
    
    def win_screen(self):
        self.sound.stop_all()
        self.sound.play_win()

        font_big = pygame.font.SysFont("arial", 60)
        font_small = pygame.font.SysFont("arial", 30)

        input_mode = False
        player_name = ""

        # 🔊 sound win (nếu có)
        # self.sound.play_win()

        while True:
            self.screen.fill((0, 0, 0))

            # ===== TITLE =====
            title = font_big.render("YOU WIN!", True, (0, 255, 0))
            self.screen.blit(title, (self.width//2 - 150, 100))

            # ===== SCORE =====
            score_txt = font_small.render(f"Score: {self.score.score}", True, (255,255,255))
            self.screen.blit(score_txt, (self.width//2 - 80, 180))

            # ===== BUTTON =====
            exit_btn = pygame.Rect(self.width//2 - 100, 250, 200, 50)
            save_btn = pygame.Rect(self.width//2 - 100, 320, 200, 50)

            pygame.draw.rect(self.screen, (100,100,100), exit_btn)
            pygame.draw.rect(self.screen, (255,255,255), exit_btn, 2)

            pygame.draw.rect(self.screen, (100,100,100), save_btn)
            pygame.draw.rect(self.screen, (255,255,255), save_btn, 2)

            txt1 = font_small.render("EXIT", True, (255,255,255))
            txt2 = font_small.render("SAVE & EXIT", True, (255,255,255))

            self.screen.blit(txt1, (exit_btn.centerx - txt1.get_width()//2, exit_btn.centery - 12))
            self.screen.blit(txt2, (save_btn.centerx - txt2.get_width()//2, save_btn.centery - 12))

            # ===== INPUT =====
            if input_mode:
                box = pygame.Rect(self.width//2 - 150, 400, 300, 50)
                pygame.draw.rect(self.screen, (255,255,255), box, 2)

                name_txt = font_small.render(player_name, True, (255,255,255))
                self.screen.blit(name_txt, (box.x + 10, box.y + 10))

            pygame.display.flip()

            # ===== EVENT =====
            for e in pygame.event.get():

                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if e.type == pygame.MOUSEBUTTONDOWN:
                    if exit_btn.collidepoint(e.pos):
                        self.sound.stop_all()           # 🔥 QUAN TRỌNG
                        pygame.mixer.music.stop()
                        return False

                    if save_btn.collidepoint(e.pos):
                        input_mode = True

                if e.type == pygame.KEYDOWN and input_mode:

                    if e.key == pygame.K_RETURN:
                        play_time = time.time() - self.start_time

                        self.leaderboard.save_score(
                            self.score.score,
                            play_time,
                            player_name
                        )
                        return False

                    elif e.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]

                    else:
                        player_name += e.unicode
    #VOLUME CONTROL
    def draw_volume_slider(self, x, y):

        bar_width = 200
        bar_height = 10

        # nền
        pygame.draw.rect(self.screen, (100,100,100),
                        (x, y, bar_width, bar_height))

        # nút kéo
        knob_x = x + int(self.volume * bar_width)
        pygame.draw.circle(self.screen, (255,255,255),
                        (knob_x, y + bar_height//2), 8)

        # text %
        font = pygame.font.SysFont("arial", 20)
        txt = font.render(f"{int(self.volume*100)}%", True, (255,255,255))
        self.screen.blit(txt, (x + bar_width + 10, y - 5))

        return pygame.Rect(x, y, bar_width, bar_height)
    def handle_volume_event(self, event, slider_rect):

        if event.type == pygame.MOUSEBUTTONDOWN:
            if slider_rect.collidepoint(event.pos):
                self.dragging_volume = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_volume = False

        elif event.type == pygame.MOUSEMOTION and self.dragging_volume:

            x = event.pos[0]
            rel_x = x - slider_rect.x

            self.volume = max(0, min(1, rel_x / slider_rect.width))

            self.sound.set_volume(self.volume)