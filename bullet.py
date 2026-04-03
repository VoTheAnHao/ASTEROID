import math
import pygame

class Bullet:
    def __init__(self, x, y, angle, vx=0, vy=0):
        rad = math.radians(angle)

        speed = 12   # 🔥 tăng tốc cho đẹp

        self.x = x
        self.y = y

        self.vx = math.cos(rad) * speed + vx
        self.vy = math.sin(rad) * speed + vy

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, (255,255,255), (int(self.x), int(self.y)), 3)

    def is_dead(self, width, height):
        return (
            self.x < 0 or self.x > width
            or self.y < 0 or self.y > height
        )