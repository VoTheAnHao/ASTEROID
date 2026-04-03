import pygame
import math
import os
from utils import resource_path


class Ship:
    def __init__(self, width, height):
        
        self.width = width
        self.height = height

        self.x = width // 2
        self.y = height // 2

        self.angle = 0

        self.radius = 20
        self.speed = 4

        self.vel_x = 0
        self.vel_y = 0

        # ===== IMAGE =====
        self.image = pygame.image.load(
            resource_path(os.path.join("asset", "rocket-removebg-preview.png"))
        ).convert_alpha()

        self.image = pygame.transform.scale(self.image, (70, 70))

        # ===== INVINCIBLE =====
        self.invincible = 120

        # ===== POWER MODE =====
        self.power_mode = False
        self.power_timer = 0
        self.power_cooldown = 0
        self.last_trigger_score = 0

    # ===== 🎮 CONTROL (UNDERTALE STYLE) =====
    def control(self, keys):
        dx = 0
        dy = 0

        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1

        # chuẩn hóa diagonal (đi chéo không nhanh hơn)
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length

        self.x += dx * self.speed
        self.y += dy * self.speed

        # 🚫 chặn không ra ngoài màn hình
        self.x = max(self.radius, min(self.width - self.radius, self.x))
        self.y = max(self.radius, min(self.height - self.radius, self.y))

    # ===== 🎯 AIM =====
    def aim(self, keys):
        if keys[pygame.K_LEFT]:
            self.angle -= 5
        if keys[pygame.K_RIGHT]:
            self.angle += 5

    # ===== UPDATE (timer only) =====
    def update(self):
        # invincible
        if self.invincible > 0:
            self.invincible -= 1

        # power mode
        if self.power_timer > 0:
            self.power_timer -= 1
            if self.power_timer == 0:
                self.power_mode = False
                self.power_cooldown = 1200

        if self.power_cooldown > 0:
            self.power_cooldown -= 1

    # ===== RESET =====
    def reset_position(self):
        self.x = self.width // 2
        self.y = self.height // 2
        self.invincible = 120

    # ===== POWER CHECK =====
    def check_power(self, score):
        if (
            score >= self.last_trigger_score + 50
            and self.power_cooldown == 0
            and not self.power_mode
        ):
            self.power_mode = True
            self.power_timer = 300
            self.last_trigger_score = score

    # ===== GUN POSITION =====
    def get_gun_position(self):
        rad = math.radians(self.angle)
        distance = 35

        return (
            self.x + math.cos(rad) * distance,
            self.y + math.sin(rad) * distance
        )

    # ===== DRAW =====
    def draw(self, screen):
        rotated = pygame.transform.rotate(self.image, -self.angle - 90)
        rect = rotated.get_rect(center=(self.x, self.y))

        if self.power_mode:
            yellow = rotated.copy()
            yellow.fill((255, 255, 0, 120), special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(yellow, rect)

        elif self.invincible > 0:
            if self.invincible % 10 < 5:
                screen.blit(rotated, rect)

        else:
            screen.blit(rotated, rect)
    def control_physical(self, keys):
        accel = 0.4

        if keys[pygame.K_w]:
            self.vel_y -= accel
        if keys[pygame.K_s]:
            self.vel_y += accel
        if keys[pygame.K_a]:
            self.vel_x -= accel
        if keys[pygame.K_d]:
            self.vel_x += accel

        # ma sát
        self.vel_x *= 0.9
        self.vel_y *= 0.9

        self.x += self.vel_x
        self.y += self.vel_y

        # chặn màn hình
        self.x = max(self.radius, min(self.width - self.radius, self.x))
        self.y = max(self.radius, min(self.height - self.radius, self.y))
    def rotate(self, direction):
    # direction: 1 (phải), -1 (trái)
        self.angle += direction * 5


    def forward(self):
        self.vel_x += math.cos(math.radians(self.angle)) * 0.5
        self.vel_y += math.sin(math.radians(self.angle)) * 0.5


    def stop(self):
        self.vel_x *= 0.95
        self.vel_y *= 0.95


    def thrust(self):
        self.forward()
    
    def hit(self):
        if self.invincible == 0:
            self.lives -= 1
            self.invincible = 60