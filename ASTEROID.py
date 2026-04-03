import os
os.environ["SDL_AUDIODRIVER"] = "coreaudio"
os.environ["SDL_VIDEODRIVER"] = "cocoa"
import pygame
import sys

from Menu import Menu
from ArcadeGame import ArcadeGame
from PhysicalGame import PhysicalGame

WIDTH, HEIGHT = 800, 600


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()

    saved_game = None

    while True:
        menu = Menu(screen, clock, WIDTH, HEIGHT, saved_game)
        action = menu.run()

        if action == "continue" and saved_game:
            game = saved_game

            # 🔥 FIX QUAN TRỌNG
            game.paused = False
            game.exit_to_menu = False

            game.countdown()

        elif action == "physical":
            game = PhysicalGame(screen, clock, WIDTH, HEIGHT)

        elif action == "arcade":
            game = ArcadeGame(screen, clock, WIDTH, HEIGHT)

        else:
            continue

        game.run()

        # 🔥 SAVE GAME
        if game.exit_to_menu:
            saved_game = game
        else:
            saved_game = None



if __name__ == "__main__":
    main()