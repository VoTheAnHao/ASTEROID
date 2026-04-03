import random
import pygame
import time
import math

class PowerUp:
    TYPES = ["bomb", "medkit", "space_bomb", "random", "totem"]

    def __init__(self, width, height, existing_totem):
        self.type = self.random_type(existing_totem)
        self.x = random.randint(50, width-50)
        self.y = random.randint(50, height-50)
        self.radius = 20
        self.active = True

        self.spawn_time = time.time()

    def random_type(self, existing_totem):
        types = self.TYPES.copy()

        # ❗ Totem chỉ tồn tại 1 cái
        if existing_totem:
            types.remove("totem")

        return random.choice(types)

    def draw(self, screen):
        colors = {
            "bomb": (255,0,0),
            "medkit": (0,255,0),
            "space_bomb": (0,0,255),
            "random": (255,255,0),
            "totem": (255,0,255)
        }

        pygame.draw.circle(screen, colors[self.type], (int(self.x), int(self.y)), self.radius)