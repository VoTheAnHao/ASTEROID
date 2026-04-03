import pygame


class Heart:
    def __init__(self):
        self.lives = 3
        self.font = pygame.font.SysFont("arial", 28)

    def lose_life(self):
        if self.lives > 0:
            self.lives -= 1

    def is_dead(self):
        return self.lives <= 0

    def draw(self, screen):
        text = self.font.render(f"Lives: {'❤️' * self.lives}", True, (255, 255, 255))
        screen.blit(text, (650, 10))