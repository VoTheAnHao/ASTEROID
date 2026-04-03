import pygame
import time
import random
from utils import resource_path


class Boss:
    def __init__(self, width, height, sound):
        self.sound = sound
        self.width = width
        self.height = height

        # ===== POSITION =====
        self.x = width // 2
        self.y = 100

        # ===== HP =====
        self.max_hp = 200
        self.hp = 200

        # ===== PHASE =====
        self.phase = 1
        self.shield = 0

        # ===== MOVEMENT =====
        self.direction = 1
        self.speed = 2

        # ===== ATTACK =====
        self.attack_type = None
        self.last_attack_type = None

        self.attack_state = "idle"
        self.attack_timer = 0

        self.attack_cooldown = 1
        self.last_skill_time = 0

        self.side = None
        self.last_side = None

        # ===== LOAD IMAGE =====
        img1 = pygame.image.load(resource_path("asset/boss-removebg-preview.png"))
        self.image_phase1 = pygame.transform.scale(img1, (160, 160))

        img2 = pygame.image.load(resource_path("asset/boss finale-removebg-preview.png"))
        self.image_phase2 = pygame.transform.scale(img2, (180, 180))

        # mặc định phase 1
        self.image = self.image_phase1

        self.blaster_img = pygame.image.load(resource_path("asset/gaster blaster-removebg-preview.png"))
        self.blaster_img = pygame.transform.scale(self.blaster_img, (140, 140))

        self.hand_img = pygame.image.load(resource_path("asset/hand-removebg-preview.png"))
        self.hand_img = pygame.transform.scale(self.hand_img, (80, 200))

    # ================= DRAW =================
    def draw(self, screen):
        rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, rect)

        # shield
        if self.shield > 0:
            pygame.draw.circle(screen, (100, 200, 255), (self.x, self.y), 90, 3)

    # ================= UPDATE =================
    def update(self, screen, player):

        hit = False

        current_time = pygame.time.get_ticks()

        # ===== PHASE CHANGE =====
        if self.hp <= 100 and self.phase == 1:
            self.phase = 2
            self.shield = 3
            self.last_shield_time = current_time
            self.attack_cooldown = 0.7
            self.image = self.image_phase2
        # ===== SHIELD REGEN =====
        if self.phase == 2:
            if current_time - self.last_shield_time > 2000:
                self.shield = min(self.shield + 1, 3)
                self.last_shield_time = current_time
        # ===== MOVE =====
        if self.phase == 1:
            self.x += self.direction * self.speed
            if self.x < 200 or self.x > self.width - 200:
                self.direction *= -1
        else:
            # random movement
            self.x += random.randint(-5, 5)
            self.x = max(150, min(self.width - 150, self.x))

        # ===== CHOOSE SKILL =====
        if time.time() - self.last_skill_time > self.attack_cooldown and self.attack_state == "idle":

            choices = [0, 1]
            if self.phase == 2:
                choices.append(2)

            if self.last_attack_type in choices:
                choices.remove(self.last_attack_type)

            self.attack_type = random.choice(choices)
            self.last_attack_type = self.attack_type

            self.last_skill_time = time.time()

        # ===== EXECUTE =====
        if self.attack_type == 0:
            hit = self.attack_blaster(screen, player)

        elif self.attack_type == 1:
            hit = self.attack_hand(screen, player)

        elif self.attack_type == 2:
            hit = self.attack_laser_grid(screen, player)

        return hit
        
    #GASTER
    def attack_blaster(self, screen, player):

        hit = False

        box_top = 300
        box_height = 200

        current_time = pygame.time.get_ticks()

        # ===== START =====
        if self.attack_state == "idle":
            self.attack_state = "charge"
            self.attack_timer = current_time
            self.played_blaster = False   # 🔥 reset sound

        # ===== CHARGE =====
        if self.attack_state == "charge":

            rect = self.blaster_img.get_rect(center=(self.x, self.y + 140))
            screen.blit(self.blaster_img, rect)

            # ⚡ warning line mờ
            offsets = [0]
            if self.phase == 2:
                offsets = [-80, 0, 80]

            for off in offsets:
                pygame.draw.line(
                    screen,
                    (100, 100, 255),
                    (self.x + off, box_top),
                    (self.x + off, box_top + box_height),
                    2
                )

            if current_time - self.attack_timer > 800:
                self.attack_state = "fire"
                self.attack_timer = current_time

        # ===== FIRE =====
        elif self.attack_state == "fire":

            # 🔊 SOUND (chỉ 1 lần)
            if not self.played_blaster:
                self.sound.play_blaster()
                self.played_blaster = True

        offsets = [0]
        if self.phase == 2:
                offsets = [-80, 0, 80]

        for off in offsets:

                # 💥 laser chính (to hơn)
            rect = pygame.Rect(
                self.x + off - 40,
                box_top,
                80,
                box_height
            )

            pygame.draw.rect(screen, (255, 255, 255), rect)

            # ✨ glow effect
            glow = pygame.Rect(
                self.x + off - 60,
                box_top,
                120,
                box_height
            )
            pygame.draw.rect(screen, (0, 255, 255), glow, 2)

            # 🎯 hit
            if rect.collidepoint(player.x, player.y):
                hit = True

        if current_time - self.attack_timer > 600:
            self.attack_state = "idle"

        return hit

    # ================= HAND =================
    def attack_hand(self, screen, player):

        hit = False

        box_left = 250
        box_top = 350
        box_width = 300
        box_height = 150

        half_width = box_width // 2

        current_time = pygame.time.get_ticks()

        # ===== CHỌN BÊN =====
        if self.attack_state == "idle":
            self.side = random.choice(["left", "right"])
            self.attack_state = "move"

            self.played_slam = False   # 🔥 reset sound

            if self.side == "left":
                self.target_x = box_left + half_width // 2
            else:
                self.target_x = box_left + half_width + half_width // 2

        # ===== MOVE =====
        elif self.attack_state == "move":

            if abs(self.x - self.target_x) > 5:
                if self.x < self.target_x:
                    self.x += 5
                else:
                    self.x -= 5
            else:
                self.attack_state = "warning"
                self.attack_timer = current_time

        # ===== WARNING (! 0.5s) =====
        elif self.attack_state == "warning":

            font = pygame.font.SysFont("arial", 30)

            if self.side == "left":
                start_x = box_left
            else:
                start_x = box_left + half_width

            count = max(1, half_width // 120)

            for i in range(count):
                x = start_x + (i + 1) * (half_width // (count + 1))
                text = font.render("!", True, (255, 0, 0))
                screen.blit(text, (x - 5, box_top - 30))

            if current_time - self.attack_timer > 500:
                self.attack_state = "slam"
                self.attack_timer = current_time
                self.hand_y = box_top - 200

        # ===== SLAM =====
        elif self.attack_state == "slam":

            if not self.played_slam:
                self.sound.play_slam()
                self.played_slam = True

            self.hand_y += 20

            directions = ["top"]

            # 💀 phase 2 thêm hướng
            if self.phase == 2:
                directions = ["top", "bottom", "left", "right"]

            count = 2 if self.phase == 2 else 1

            for direction in directions:

                for i in range(count):

                    # ===== TOP =====
                    if direction == "top":
                        x = box_left + (i + 1) * (box_width // (count + 1))
                        y = self.hand_y
                        rect = self.hand_img.get_rect(midtop=(x, y))

                    # ===== BOTTOM =====
                    elif direction == "bottom":
                        x = box_left + (i + 1) * (box_width // (count + 1))
                        y = box_top + box_height - self.hand_y + box_top
                        rect = self.hand_img.get_rect(midbottom=(x, y))

                    # ===== LEFT =====
                    elif direction == "left":
                        x = self.hand_y
                        y = box_top + (i + 1) * (box_height // (count + 1))
                        rect = self.hand_img.get_rect(midleft=(x, y))

                    # ===== RIGHT =====
                    elif direction == "right":
                        x = box_left + box_width - self.hand_y + box_left
                        y = box_top + (i + 1) * (box_height // (count + 1))
                        rect = self.hand_img.get_rect(midright=(x, y))

                    screen.blit(self.hand_img, rect)

                    # 🎯 HIT CHECK
                    if rect.collidepoint(player.x, player.y):
                        hit = True

            if pygame.time.get_ticks() - self.attack_timer > 700:
                self.attack_state = "idle"
                self.hand_y = box_top - 200

    # ================= LASER GRID =================
    def attack_laser_grid(self, screen, player):

        hit = False

        for i in range(6):
            x = 150 + i * 80

            pygame.draw.line(
                screen,
                (255, 255, 255),
                (x, 300),
                (x, self.height),
                8
            )

            if abs(player.x - x) < 20:
                hit = True

        return hit

    # ================= HEALTH BAR =================
    def draw_health_bar(self, screen):

        bar_width = 400
        bar_height = 20

        x = self.width // 2 - bar_width // 2
        y = self.height - 40

        pygame.draw.rect(screen, (100, 0, 0), (x, y, bar_width, bar_height))

        current = int(bar_width * (self.hp / self.max_hp))
        pygame.draw.rect(screen, (255, 0, 0), (x, y, current, bar_height))

        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)