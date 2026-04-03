import pygame

class Score:
    def __init__(self):
        self.score = 0   # 🔥 BẮT BUỘC phải có dòng này

        self.font = pygame.font.SysFont("arial", 24)

    def add(self, points):
        self.score += points

    def draw(self, screen):
        text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(text, (10, 40))