import pygame
import random
import math


class Asteroid:
    def __init__(self, width, height, size=3, x=None, y=None):
        self.width = width
        self.height = height

        # size: 3 = to, 2 = vừa, 1 = nhỏ
        self.size = size

        # vị trí
        self.x = x if x is not None else random.randint(0, width)
        self.y = y if y is not None else random.randint(0, height)

        # tốc độ (nhỏ → nhanh hơn)
        speed = random.uniform(1, 2) + (4 - size)

        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # bán kính theo size
        self.radius = size * 15 + random.randint(5, 10)

        # tạo shape bất quy tắc
        self.points = self.generate_shape()

    def generate_shape(self):
        points = []
        num_points = random.randint(8, 12)

        for i in range(num_points):
            angle = (2 * math.pi / num_points) * i
            r = self.radius + random.randint(-5, 5)

            x = math.cos(angle) * r
            y = math.sin(angle) * r

            points.append((x, y))

        return points

    def move(self):
        self.x = (self.x + self.vx) % self.width
        self.y = (self.y + self.vy) % self.height

    def draw(self, screen):
        transformed_points = []

        for px, py in self.points:
            transformed_points.append((self.x + px, self.y + py))

        pygame.draw.polygon(screen, (255, 255, 255), transformed_points, 2)

    # 💥 TÁCH THIÊN THẠCH
    def split(self):
        if self.size > 1:
            return [
                Asteroid(self.width, self.height, self.size - 1, self.x, self.y),
                Asteroid(self.width, self.height, self.size - 1, self.x, self.y)
            ]
        return []