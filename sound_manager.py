import pygame
from utils import resource_path

class SoundManager:
    def __init__(self):

        pygame.mixer.init()

        # ===== MUSIC =====
        self.menu_music = resource_path("asset/waiting.mp3")
        self.arcade_music = resource_path("asset/normal.mp3")
        self.boss_music = resource_path("asset/boss theme.mp3")

        # ===== SFX =====
        self.shoot = pygame.mixer.Sound(resource_path("asset/laser.mp3"))
        self.death = pygame.mixer.Sound(resource_path("asset/Death Sound.mp3"))
        self.gameover = pygame.mixer.Sound(resource_path("asset/Game Over.mp3"))
        self.slam = pygame.mixer.Sound(resource_path("asset/SLASH Sound.mp3"))
        self.blaster = pygame.mixer.Sound(resource_path("asset/boss weapon sound.mp3"))

        # volume
        self.shoot.set_volume(0.4)
        self.slam.set_volume(0.6)
        self.blaster.set_volume(0.6)

    # ===== MUSIC =====
    def play_music(self, music_file, loop=True):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1 if loop else 0)

    def stop_music(self):
        pygame.mixer.music.stop()

    # ===== SFX =====
    def play_shoot(self):
        self.shoot.play()

    def play_death(self):
        self.death.play()

    def play_gameover(self):
        self.gameover.play()

    def play_slam(self):
        self.slam.play()

    def play_blaster(self):
        self.blaster.play()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

        self.shoot.set_volume(volume)
        self.death.set_volume(volume)
        self.gameover.set_volume(volume)
        self.slam.set_volume(volume)
        self.blaster.set_volume(volume)
    
    def stop_all(self):
        pygame.mixer.music.stop()     # stop music
        pygame.mixer.stop()